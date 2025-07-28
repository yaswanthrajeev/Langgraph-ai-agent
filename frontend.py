# Updated frontend.py for Docker deployment
import streamlit as st
import os
import time

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

# Use environment variable for API URL, fallback to localhost for local development
API_URL = os.getenv("API_URL", "http://127.0.0.1:9999/chat")

# Display current API URL for debugging
st.sidebar.write(f"API URL: {API_URL}")

if st.button("Ask Agent!"):
    if user_query.strip():
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
        print("DEBUG API_URL:", API_URL)  # Debug print
        
        # Add loading spinner
        with st.spinner('Processing your request...'):
            try:
                # Add retry logic with exponential backoff
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = requests.post(
                            API_URL, 
                            json=payload, 
                            timeout=60,  # 60 second timeout
                            headers={'Content-Type': 'application/json'}
                        )
                        break  # If successful, break out of retry loop
                    except requests.exceptions.ConnectionError as e:
                        if attempt < max_retries - 1:
                            st.warning(f"Connection attempt {attempt + 1} failed, retrying in {2**attempt} seconds...")
                            time.sleep(2**attempt)  # Exponential backoff
                            continue
                        else:
                            raise e
                
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
                    
            except requests.exceptions.ConnectionError as e:
                st.error(f"Connection failed: Cannot connect to backend service. Please ensure the backend is running.")
                st.error(f"Technical details: {e}")
            except requests.exceptions.Timeout as e:
                st.error(f"Request timed out: The request took too long to complete.")
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
    else:
        st.warning("Please enter a query!")