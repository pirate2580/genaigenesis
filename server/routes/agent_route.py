from flask import Blueprint, jsonify, request
import asyncio
from playwright.async_api import async_playwright
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../services/ai_agent')))
from run_ai_agent import run_ai_agent


api_blueprint = Blueprint("agent", __name__)

@api_blueprint.route("/browser_control", methods=["POST", "GET"])
def browser_control():
    # TODO assumes certain format for front end json
    data = request.json
    question = data.get('question')
    asyncio.run(run_ai_agent(question))
