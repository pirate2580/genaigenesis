import base64
import asyncio
import os
from langchain_core.runnables import chain as chain_decorator

# Some javascript we will run on each step
# to take a screenshot of the page, select the
# elements to annotate, and add bounding boxes

mark_page_path = os.path.join(os.path.dirname(__file__), "mark_page.js")

with open(mark_page_path) as f:
    mark_page_script = f.read()


@chain_decorator
async def mark_page(page):
  await page.evaluate(mark_page_script)
  for _ in range(10):
    try:
      bboxes = await page.evaluate("markPage()")
      break
    except Exception:
      # May be loading...
      asyncio.sleep(3)
  screenshot = await page.screenshot()
  # Ensure the bboxes don't follow us around
  await page.evaluate("unmarkPage()")
  return {
      "img": base64.b64encode(screenshot).decode(),
      "bboxes": bboxes,
  }