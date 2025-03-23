"""
File containing all AI Agent tools to interact with browser

TODO: add more tools to screenshot images ie if someone wants to get specific images for a research report

TODO: add tool to summarize website, use another smaller LLM for that, webscrape w BeautifulSoup and then just throw to LLM with good prompt
"""
import os
import random
import asyncio
import platform
from definitions import AgentState
from langchain_google_genai import ChatGoogleGenerativeAI
import pyttsx3
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
# Use gTTS for better async compatibility
from gtts import gTTS
from io import BytesIO
import pygame

# Load environment variables
load_dotenv()

# function to add a random delay to not get detected by google antibot
# async def random_delay(min_delay=0.5, max_delay=1.5):
#   await asyncio.sleep(random.uniform(min_delay, max_delay))


async def click(state: AgentState):
  # - Click [Numerical_Label]
  page = state["page"]
  click_args = state["prediction"]["args"]
  if click_args is None or len(click_args) != 1:
      return f"Failed to click bounding box labeled as number {click_args}"
  bbox_id = click_args[0]
  bbox_id = int(bbox_id)
  try:
      bbox = state["bboxes"][bbox_id]
  except Exception:
      return f"Error: no bbox for : {bbox_id}"
  x, y = bbox["x"], bbox["y"]


  await page.mouse.click(x, y)

  return f"Clicked {bbox_id}"


async def type_text(state: AgentState):

  page = state["page"]
  type_args = state["prediction"]["args"]
  if type_args is None or len(type_args) != 2:
      return (
          f"Failed to type in element from bounding box labeled as number {type_args}"
      )
  bbox_id = type_args[0]
  bbox_id = int(bbox_id)
  bbox = state["bboxes"][bbox_id]
  x, y = bbox["x"], bbox["y"]

  text_content = type_args[1]

  await page.mouse.click(x, y)
  # Check if MacOS
  select_all = "Meta+A" if platform.system() == "Darwin" else "Control+A"
  await page.keyboard.press(select_all)
  await page.keyboard.press("Backspace")
  # await page.keyboard.type(text_content)
  await page.keyboard.type(text_content, delay=random.uniform(50, 150)) 
  await page.keyboard.press("Enter")

  # if random.random() < 0.5:
  #       await random_mouse_move_away(page)
        
  return f"Typed {text_content} and submitted"


async def scroll(state: AgentState):
  page = state["page"]
  scroll_args = state["prediction"]["args"]
  if scroll_args is None or len(scroll_args) != 2:
      return "Failed to scroll due to incorrect arguments."

  target, direction = scroll_args

  if target.upper() == "WINDOW":
    scroll_amount = random.randint(450, 550)  # Randomize scroll distance
    scroll_direction = (
        -scroll_amount if direction.lower() == "up" else scroll_amount
    )

    # slow down scroll distance
    for _ in range(random.randint(3, 6)):
      await page.evaluate(f"window.scrollBy(0, {scroll_direction / 5})")
  else:
      # Scrolling within a specific element
      # scroll_amount = 200
      scroll_amount = random.randint(150, 250)  # Randomize scroll distance to avoid bot detection
      scroll_direction = (
        -scroll_amount if direction.lower() == "up" else scroll_amount
      )
      target_id = int(target)
      bbox = state["bboxes"][target_id]
      x, y = bbox["x"], bbox["y"]

      # await page.mouse.move(x, y)

      # slow down mouse movement
      # await humanize_mouse_move(page, x, y)
      for _ in range(random.randint(3, 6)):  # Scroll in steps
        await page.mouse.wheel(0, scroll_direction / 5)

  return f"Scrolled {direction} in {'window' if target.upper() == 'WINDOW' else 'element'}"


async def wait(state: AgentState):
  sleep_time = 5
  await asyncio.sleep(sleep_time)
  return f"Waited for {sleep_time}s."


async def go_back(state: AgentState):
  page = state["page"]
  await page.go_back()
  return f"Navigated back a page to {page.url}."


async def to_google(state: AgentState):
  page = state["page"]
  await page.goto("https://www.google.com/")
  return "Navigated to google.com."

async def generate_narration_tts(state: AgentState):
    prompt = (
        f"Generate a short, conversational narration for an AI agent action. "
        f"The agent executed the instruction {state}. "
        f"Keep it friendly and natural."
    )
    
    narration_llm_small = ChatGoogleGenerativeAI(model="gemini-2.0-flash",
                                              google_api_key=os.getenv("GEMINI_API_KEY"))
    messages = [HumanMessage(content=prompt)]
    
    narration_response = await narration_llm_small.ainvoke(messages)
    narration = narration_response.content
    
    # Create speech in memory
    tts = gTTS(narration, lang='en', tld='co.uk')  # British English
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)

    # Play audio using pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load(fp)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)
    
    await asyncio.sleep(1)  # Short pause after narration
    return "LLM narration successful"


# async def generate_narration_tts(state: AgentState):
#     prompt = (
#         f"Generate a short, conversational narration for an AI agent action. "
#         f"The agent executed the instruction {state}. "
#         f"Keep it friendly and natural."
#     )
    
#     narration_llm_small = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GEMINI_API_KEY"))
#     messages = [HumanMessage(content=prompt)]
    
#     # Correctly invoke the model with messages
#     narration_response = await narration_llm_small.ainvoke(messages)  # Use async invoke
#     narration = narration_response.content  # Extract the content from the response
    
#     narration_response = await narration_llm_small.ainvoke(messages)
#     narration = narration_response.content

#     # Run blocking TTS in executor to avoid event loop conflicts
#     def _speak():
#         engine = pyttsx3.init()
#         engine.setProperty('rate', 120)
#         engine.say(narration)
#         engine.runAndWait()
#         engine.stop()
#         del engine

#     loop = asyncio.get_event_loop()
#     await loop.run_in_executor(None, _speak)

#     await asyncio.sleep(2)  # Fixed: use async sleep instead of wait()
#     return "LLM narration successful"

