"""
Naoroj:

File with helper functions used in run_ai_agent.py
These functions overall build the AI agent.
"""

import asyncio
import re
import os
import platform
from dotenv import load_dotenv
from playwright.async_api import TimeoutError


from langchain import hub
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, StateGraph

from annotate import mark_page
from definitions import AgentState
from tools import click, type_text, scroll, wait, go_back, to_google
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()

# Function to mark page from js
async def annotate(state):
    marked_page = await mark_page.with_retry().ainvoke(state["page"])
    return {**state, **marked_page}

# Format bounding boxes obtained from JS script to mark page
def format_descriptions(state):
    labels = []
    for i, bbox in enumerate(state["bboxes"]):
        text = bbox.get("ariaLabel") or bbox["text"]
        el_type = bbox.get("type")
        labels.append(f'{i} (<{el_type}/>): "{text}"')

    bbox_descriptions = "\nValid Bounding Boxes:\n" + "\n".join(labels)
    return {**state, "bbox_descriptions": bbox_descriptions}

# Helper function to parse LLM output
def parse(text: str) -> dict:
    action_prefix = "Action: "
    if not text.strip().split("\n")[-1].startswith(action_prefix):
        return {"action": "retry", "args": f"Could not parse LLM Output: {text}"}

    action_block = text.strip().split("\n")[-1]
    action_str = action_block[len(action_prefix):]
    split_output = action_str.split(" ", 1)

    action, action_input = (split_output[0], None) if len(split_output) == 1 else split_output
    action = action.strip()
    
    if action_input is not None:
        action_input = [inp.strip().strip("[]") for inp in action_input.strip().split(";")]
    
    return {"action": action, "args": action_input}

# Node to update LLM observations
def update_scratchpad(state: AgentState):
    """Updates the scratchpad so the agent is aware of its previous steps."""
    old = state.get("scratchpad")
    if old:
        txt = old[0].content
        last_line = txt.rsplit("\n", 1)[-1]
        step = int(re.match(r"\d+", last_line).group()) + 1
    else:
        txt = "Previous action observations:\n"
        step = 1

    txt += f"\n{step}. {state['observation']}"
    return {**state, "scratchpad": [SystemMessage(content=txt)]}

# Node to select the proper tool to use: TODO don't end
def select_tool(state: AgentState):
    """Determines which tool to use based on the agent's prediction."""
    action = state["prediction"]["action"]
    if action == "ANSWER":
        return END
    if action == "retry":
        return "agent"
    return action

# Function to create LangGraph Agent with Gemini AI
def create_graph(update_scratchpad, select_tool):
    """Creates and compiles the StateGraph with tools and conditional logic."""
    prompt = hub.pull("wfh/web-voyager")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GEMINI_API_KEY)
    
    agent = annotate | RunnablePassthrough.assign(
        prediction=format_descriptions | prompt | llm | StrOutputParser() | parse
    )
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("agent", agent)
    graph_builder.add_edge(START, "agent")
    graph_builder.add_node("update_scratchpad", update_scratchpad)
    graph_builder.add_edge("update_scratchpad", "agent")

    # Tool definitions
    tools = {
        "Click": click,
        "Type": type_text,
        "Scroll": scroll,
        "Wait": wait,
        "GoBack": go_back,
        "Google": to_google,
    }

    # Add tools as nodes and connect them
    for node_name, tool in tools.items():
        graph_builder.add_node(
            node_name,
            RunnableLambda(tool) | (lambda observation: {"observation": observation}),
        )
        graph_builder.add_edge(node_name, "update_scratchpad")

    # Add conditional edges for tool selection logic
    graph_builder.add_conditional_edges("agent", select_tool)

    return graph_builder.compile(interrupt_before=["tools"])

# Function to call the AI agent on a question

async def call_agent(graph, question: str, page, max_steps: int = 150):
    """Runs the graph with the given question and page,
    ensuring stability before actions are taken."""
    
    try:
        await page.wait_for_load_state("domcontentloaded")
    except TimeoutError:
        print("Page load timed out, but continuing execution.")

    event_stream = graph.astream(
        {
            "page": page,
            "input": question,
            "scratchpad": [],
        },
        {
            "recursion_limit": max_steps,
        },
    )

    final_answer = None
    steps = []
    async for event in event_stream:
        if "agent" not in event:
            continue
        pred = event["agent"].get("prediction") or {}
        action = pred.get("action")
        action_input = pred.get("args")

        # Ensure the page is still available before typing/clicking
        if not page.is_closed():
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=5000)
            except TimeoutError:
                print("Page load state check timed out.")

        steps.append(f"{len(steps) + 1}. {action}: {action_input}")
        print("\n".join(steps))

        if "ANSWER" in action:
            final_answer = action_input[0]
            break

    print("Process finished. The browser tab will remain open.")
    return final_answer
