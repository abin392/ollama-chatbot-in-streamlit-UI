import os
import json
import requests
import streamlit as st

st.title("Ollama Local Chat")

# Dynamic base URL: Uses environment variable if set on Render, else defaults to local
OLLAMA_HOST = os.getenv("OLLAMA_URL", "http://localhost:11434")

# Initialize chat history to persist across reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capture user input
if prompt := st.chat_input("Message Ollama..."):
    # Display user input and save to session state
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            
            def generate_response():
                url = f"{OLLAMA_HOST}/api/chat"
                payload = {
                    "model": "llama3.2:1b",
                    "messages": st.session_state.messages,
                    "stream": True
                }
                try:
                    response = requests.post(url, json=payload, stream=True)
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line:
                            chunk = json.loads(line.decode("utf-8"))
                            yield chunk.get("message", {}).get("content", "")
                except requests.exceptions.RequestException as e:
                    yield f"**Error connecting to Ollama ({OLLAMA_HOST}):** {str(e)}"

            full_response = st.write_stream(generate_response())
        
    # Save the assistant's complete response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})