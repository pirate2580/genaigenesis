from fastapi import FastAPI
from pydantic import BaseModel
import cohere

app = FastAPI()
co = cohere.Client("API-KEY")

class ChatRequest(BaseModel):
    message: str
    chat_history: list = []  # Ensure it's a list, default to empty

@app.post("/chat")
async def chat(request: ChatRequest):
    response = co.chat(
        message=request.message,
        chat_history=request.chat_history  # Pass list, not string
    )
    return {"response": response.text}
