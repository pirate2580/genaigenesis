"""
File that contains definitions that agent needs

Note: Bounding box class is for the bounding boxes found from JS script. Used later in pipeline to help AI agent know where to click 

Other class defns are standard
"""

from typing import List, Optional
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, SystemMessage
from playwright.async_api import Page

# bounding box definition that we get from mark_page.js
class BBox(TypedDict):
  x: float
  y: float
  text: str
  type: str
  ariaLabel: str

# AI Agent prediction definition
class Prediction(TypedDict):
  action: str
  args: Optional[List[str]]

# This represents the state of the agent
# as it proceeds through execution
class AgentState(TypedDict):
  page: Page  # The Playwright web page lets us interact with the web environment
  input: str  # User request
  img: str  # b64 encoded screenshot
  bboxes: List[BBox]  # The bounding boxes from the browser annotation function
  prediction: Prediction  # The Agent's output
  # A system message (or messages) containing the intermediate steps
  scratchpad: List[BaseMessage]
  observation: str  # The most recent response from a tool