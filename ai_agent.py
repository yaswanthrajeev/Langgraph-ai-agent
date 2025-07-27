#set up api key
import os
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

#set llm or tools
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent
from langchain_core.messages.ai import AIMessage
from langchain_core.messages import HumanMessage, SystemMessage

def get_resposne_from_ai_agent(llm_id, messages, allow_search, system_prompt, provider):
    if provider == "groq":
        llm = ChatGroq(model=llm_id)
    elif provider == "OpenAI":
        llm = ChatOpenAI(model=llm_id)
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    tools = [TavilySearch(max_results=2)] if allow_search else []

    # Create the agent without state_modifier
    agent = create_react_agent(
        model=llm,
        tools=tools
    )
    
    # Convert dict messages to LangChain message objects
    langchain_messages = []
    
    # Add system prompt as the first message if provided
    if system_prompt and system_prompt.strip():
        langchain_messages.append(SystemMessage(content=system_prompt))
    
    # Convert user messages
    for msg in messages:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=str(msg["content"])))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=str(msg["content"])))
        elif msg["role"] == "system":
            langchain_messages.append(SystemMessage(content=str(msg["content"])))
    
    state = {
        "messages": langchain_messages
    }
    
    print("DEBUG STATE:", state)  # Debug print
    print("DEBUG MESSAGE TYPES:", [type(msg) for msg in langchain_messages])
    print("DEBUG MESSAGE CONTENTS:", [{"type": type(msg).__name__, "content": msg.content} for msg in langchain_messages])
    
    try:
        response = agent.invoke(state)
        messages = response.get("messages", [])
        ai_messages = [message.content for message in messages if isinstance(message, AIMessage)]
        return ai_messages[-1] if ai_messages else "No response generated"
    except Exception as e:
        print(f"Error in agent invocation: {e}")
        raise e