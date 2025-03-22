"""
File containing all AI Agent tools to interact with browser

TODO: add more tools to screenshot images ie if someone wants to get specific images for a research report

TODO: add tool to summarize website, use another smaller LLM for that, webscrape w BeautifulSoup and then just throw to LLM with good prompt
"""

import random
import asyncio
import platform
from definitions import AgentState

# function to add a random delay to not get detected by google antibot
async def random_delay(min_delay=0.5, max_delay=1.5):
  await asyncio.sleep(random.uniform(min_delay, max_delay))

# helper function to hover for some time
async def small_hover(page, duration=None):
  """Optional hover or idle time to appear more human."""
  await random_delay(0.5, 1.0)
  if duration is None:
      duration = random.uniform(0.2, 1.0)
  await asyncio.sleep(duration)

async def random_mouse_move_away(page):
    """
    Move the mouse off the target area randomly, 
    simulating human 'drift' or checking another part of the screen.
    """
    curr_mouse_pos = await page.mouse.position()
    # Move the mouse some random offset away
    offset_x = random.uniform(-200, 200)
    offset_y = random.uniform(-200, 200)
    steps = random.randint(10, 20)
    for i in range(steps):
        await page.mouse.move(
            curr_mouse_pos['x'] + offset_x * i / steps,
            curr_mouse_pos['y'] + offset_y * i / steps
        )
        await asyncio.sleep(random.uniform(0.01, 0.05))

# Helper function for click to make moving mouse slower to prevent google detection
last_mouse_position = (0, 0)

async def get_mouse_position(page):
    return await page.evaluate("""
        () => new Promise(resolve => {
            document.addEventListener('mousemove', event => {
                resolve({ x: event.clientX, y: event.clientY });
            }, { once: true });
        })
    """)

async def random_mouse_move_away(page):
    curr_mouse_pos = await get_mouse_position(page)  # Fetch position from browser
    new_x = curr_mouse_pos["x"] + 100
    new_y = curr_mouse_pos["y"] + 100

    await page.mouse.move(new_x, new_y)


async def humanize_mouse_move(page, x, y):
    await random_delay(0.3, 1.0)
    global last_mouse_position
    last_x, last_y = last_mouse_position  # Use stored position

    # Move the mouse
    await page.mouse.move(x, y)
    
    # Update stored position
    last_mouse_position = (x, y)


async def click(state: AgentState):
  # - Click [Numerical_Label]
  # random delay to simulate thinking
  await random_delay(0.3, 1.0)
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

  # make mouse move slower
  await humanize_mouse_move(page, x, y)

  # Hover slightly
  await small_hover(page, duration=random.uniform(0.3, 1.2))

  await page.mouse.click(x, y)
  await small_hover(page, duration=random.uniform(0.2, 0.5))

  if random.random() < 0.5:
    await random_mouse_move_away(page)

  return f"Clicked {bbox_id}"


async def type_text(state: AgentState):
  await random_delay(0.5, 1.5)  # 'Thinking' before typing

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

  await humanize_mouse_move(page, x, y)
  await small_hover(page, duration=random.uniform(0.2, 0.8))


  text_content = type_args[1]

  await random_delay(0.5, 1)  # Mimics thinking before typing
  await page.mouse.click(x, y)
  await random_delay(0.1, 0.2)
  # Check if MacOS
  select_all = "Meta+A" if platform.system() == "Darwin" else "Control+A"
  await page.keyboard.press(select_all)
  await page.keyboard.press("Backspace")
  # await page.keyboard.type(text_content)
  await page.keyboard.type(text_content, delay=random.uniform(50, 150)) 
  await page.keyboard.press("Enter")

  if random.random() < 0.5:
        await random_mouse_move_away(page)
        
  return f"Typed {text_content} and submitted"


async def scroll(state: AgentState):
  await random_delay(0.3, 1.0)

  page = state["page"]
  scroll_args = state["prediction"]["args"]
  if scroll_args is None or len(scroll_args) != 2:
      return "Failed to scroll due to incorrect arguments."

  target, direction = scroll_args
  scroll_direction = (
        -scroll_amount if direction.lower() == "up" else scroll_amount
    )

  if target.upper() == "WINDOW":
    scroll_amount = random.randint(450, 550)  # Randomize scroll distance

    # slow down scroll distance
    for _ in range(random.randint(3, 6)):
      await page.evaluate(f"window.scrollBy(0, {scroll_direction / 5})")
      await random_delay(0.1, 0.2)
  else:
      # Scrolling within a specific element
      # scroll_amount = 200
      scroll_amount = random.randint(150, 250)  # Randomize scroll distance to avoid bot detection
      target_id = int(target)
      bbox = state["bboxes"][target_id]
      x, y = bbox["x"], bbox["y"]

      # await page.mouse.move(x, y)

      # slow down mouse movement
      await humanize_mouse_move(page, x, y)
      for _ in range(random.randint(3, 6)):  # Scroll in steps
        await page.mouse.wheel(0, scroll_direction / 5)
        await random_delay(0.1, 0.2)

  return f"Scrolled {direction} in {'window' if target.upper() == 'WINDOW' else 'element'}"


async def wait(state: AgentState):
  await random_delay(0.3, 1.0)

  sleep_time = 5
  await asyncio.sleep(sleep_time)
  return f"Waited for {sleep_time}s."


async def go_back(state: AgentState):
  await random_delay(0.3, 1.0)

  page = state["page"]
  await page.go_back()
  return f"Navigated back a page to {page.url}."


async def to_google(state: AgentState):
  await random_delay(0.3, 1.0)

  page = state["page"]
  await page.goto("https://www.google.com/")
  return "Navigated to google.com."