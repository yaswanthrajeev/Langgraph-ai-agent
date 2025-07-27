from pydantic import BaseModel
from typing import List, Dict, Any

class Message(BaseModel):
    role: str
    content: str

class RequestState(BaseModel):
    model_name: str
    model_provider: str
    system_prompt: str
    messages: List[Message]  # Use proper Message objects
    allow_search: bool

from fastapi import FastAPI
from ai_agent import get_resposne_from_ai_agent

ALLOWED_MODEL_NAMES = ["gpt-4o-mini", "llama-3.3-70b-versatile", "mixtral-8x7b-32768"]
app = FastAPI(title="Langgraoh ai agent")

@app.post("/chat")
def chat_endpoint(request: RequestState):
    if request.model_name not in ALLOWED_MODEL_NAMES:
        return {"error": "model not allowed"}

    llm_id = request.model_name
    # Convert Pydantic models to dicts
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    allow_search = request.allow_search
    system_prompt = request.system_prompt
    provider = request.model_provider

    try:
        response = get_resposne_from_ai_agent(llm_id, messages, allow_search, system_prompt, provider)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9999)