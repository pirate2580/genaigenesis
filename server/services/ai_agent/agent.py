"""
Naoroj:

File with helper functions used in run_ai_agent.py
These functions overall build the ai agent
"""

from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.runnables import RunnableLambda
from langgraph.graph import END, START, StateGraph
from langchain_openai import ChatOpenAI
from annotate import mark_page
from definitions import AgentState
from tools import click, type_text, scroll, wait, go_back, to_google
from IPython import display
from playwright.async_api import async_playwright
import re
import os
from dotenv import load_dotenv
load_dotenv()

# Function to mark page from js
async def annotate(state):
  marked_page = await mark_page.with_retry().ainvoke(state["page"])
  return {**state, **marked_page}

# Format bounding boxes obtained from js script to mark page
def format_descriptions(state):
  labels = []
  for i, bbox in enumerate(state["bboxes"]):
    text = bbox.get("ariaLabel") or ""
    if not text.strip():
        text = bbox["text"]
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

  action_str = action_block[len(action_prefix) :]
  split_output = action_str.split(" ", 1)
  if len(split_output) == 1:
      action, action_input = split_output[0], None
  else:
      action, action_input = split_output
  action = action.strip()
  if action_input is not None:
      action_input = [
          inp.strip().strip("[]") for inp in action_input.strip().split(";")
      ]
  return {"action": action, "args": action_input}

# node to update LLMs observations
def update_scratchpad(state: AgentState):
    """After a tool is invoked, we want to update
    the scratchpad so the agent is aware of its previous steps"""
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

# node to select the proper tool to use
def select_tool(state: AgentState):
    # Any time the agent completes, this function
    # is called to route the output to a tool or
    # to the end user.
    action = state["prediction"]["action"]
    if action == "ANSWER":
        return END
    if action == "retry":
        return "agent"
    return action

# Function to create LangGraph Agent
def create_graph(update_scratchpad, select_tool):
    """Creates and compiles the StateGraph with tools and conditional logic."""
    prompt = hub.pull("wfh/web-voyager")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4-turbo", max_tokens=4096)
    
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

    return graph_builder.compile()

# Function to call the AI agent on a question
async def call_agent(graph, question: str, page, max_steps: int = 150):
    """Runs the graph with the given question and page, returning the agent's response."""
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
        steps.append(f"{len(steps) + 1}. {action}: {action_input}")
        print("\n".join(steps))
        if "ANSWER" in action:
            final_answer = action_input[0]
            break
    return final_answer