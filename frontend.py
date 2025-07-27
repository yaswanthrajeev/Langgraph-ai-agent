# if you dont use pipenv uncomment the following:
# from dotenv import load_dotenv
# load_dotenv()

#Step1: Setup UI with streamlit (model provider, model, system prompt, web_search, query)
import streamlit as st

st.set_page_config(page_title="LangGraph Agent UI", layout="centered")
st.title("AI Chatbot Agents")
st.write("Create and Interact with the AI Agents!")

system_prompt = st.text_area("Define your AI Agent: ", height=70, placeholder="Type your system prompt here...")

MODEL_NAMES_GROQ = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]
MODEL_NAMES_OPENAI = ["gpt-4o-mini"]

provider = st.radio("Select Provider:", ("groq", "OpenAI"))

if provider == "groq":
    selected_model = st.selectbox("Select Groq Model:", MODEL_NAMES_GROQ)
elif provider == "OpenAI":
    selected_model = st.selectbox("Select OpenAI Model:", MODEL_NAMES_OPENAI)

allow_web_search = st.checkbox("Allow Web Search")

user_query = st.text_area("Enter your query: ", height=150, placeholder="Ask Anything!")

API_URL = "http://127.0.0.1:9999/chat"

if st.button("Ask Agent!"):
    if user_query.strip():
        #Step2: Connect with backend via URL
        import requests

        payload = {
            "model_name": selected_model,
            "model_provider": provider,
            "system_prompt": system_prompt if system_prompt else "",
            "messages": [
                {"role": "user", "content": str(user_query).strip()}
            ],
            "allow_search": allow_web_search
        }

        print("DEBUG PAYLOAD:", payload)  # Debug print
        
        try:
            response = requests.post(API_URL, json=payload)
            print("DEBUG RESPONSE STATUS:", response.status_code)
            print("DEBUG RESPONSE TEXT:", response.text)
            
            if response.status_code == 200:
                response_data = response.json()
                if "error" in response_data:
                    st.error(f"Error: {response_data['error']}")
                else:
                    st.subheader("Agent Response")
                    # Handle both old and new response formats
                    if "response" in response_data:
                        st.markdown(f"**Final Response:** {response_data['response']}")
                    else:
                        st.markdown(f"**Final Response:** {response_data}")
            else:
                st.error(f"HTTP Error {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
    else:
        st.warning("Please enter a query!")