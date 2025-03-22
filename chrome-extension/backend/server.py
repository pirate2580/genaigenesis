import google.generativeai as genai
from fastapi import FastAPI
from pydantic import BaseModel

# Configure API key
genai.configure(api_key="API-KEY")

# Initialize FastAPI app
app = FastAPI()

# Request model for dynamic input
class ChatRequest(BaseModel):
    message: str
    model: str = "gemini-1.5-flash"  # Default model

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Validate model name
        available_models = ["gemini-1.5-flash", "gemini-1.5-pro"]
        if request.model not in available_models:
            return {"error": "Invalid model. Use 'gemini-1.5-flash' or 'gemini-1.5-pro'."}

        # Create model instance
        model = genai.GenerativeModel(request.model)

        # Generate response
        response = model.generate_content(request.message)
        return {"response": response.text}

    except Exception as e:
        return {"error": str(e)}
