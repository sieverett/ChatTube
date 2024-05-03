import pandas as pd
from utils_extension import build_rag_chain
from utils import speak, list_cloned_voices                            
import streamlit as st
import os
import sys
from dotenv import load_dotenv
sys.path.append('../')

load_dotenv('.env')

st.set_page_config(page_title="Knowledge",
                   page_icon="🔘", layout="centered", initial_sidebar_state="auto", menu_items=None)
# openai.api_key = st.secrets.openai_key
st.title("Knowledge 💬")
# st.info(
#     "Chat with the Presenter", icon="📃")

# st.text(os.getenv("APP_ROOT_DIR"))

if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant",
         "content": "Ask me a question about my presentation!"}
    ]

if "chat_engine" not in st.session_state.keys():  # Initialize the chat engine
    st.session_state.chat_engine = ""

cloned_dict = list_cloned_voices()
cloned_names = list(cloned_dict.keys())
# cloned_names_caps=capitalize_names(cloned_names)
df = pd.read_csv("RI/SLT_playlist_info.csv")
# Extract names for the dropdown

with st.sidebar:
    names = df.presenter.tolist()
    cloned_names = sorted([n for n in cloned_names if n in names])
    selected_name = st.selectbox("Select Presenter", cloned_names)

if selected_name:

    st.session_state.messages = [
        {"role": "assistant",
         "content": "Ask me a question about the presentation!"}
    ]
    # get video link
    with st.expander("Watch Video 📺", expanded=False):
        link_dict = {k: v for k, v in zip(df.presenter, df.link)}
        # Replace with your CSV file path
        link_dict = {k: v for k, v in zip(df.presenter, df.link)}
        try:
            video_link = link_dict[selected_name]
            _, container, _ = st.columns([20, 40, 20])
            container.video(video_link)
        except KeyError as e:
            st.write(f"You selected: {selected_name}")
            st.write('No video available.')
            st.write(e)

    # @st.cache_resource(show_spinner=False)
    def load_rag_chat():
        # with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        rag_chain = build_rag_chain(selected_name)
        return rag_chain

    st.session_state.chat_engine = load_rag_chat()

    # Prompt for user input and save to chat history
    if prompt := st.chat_input("Your question"):
        st.session_state.messages.append({"role": "user", "content": prompt})

    for message in st.session_state.messages:  # Display the prior chat messages
        if message["role"] == "user":
            with st.chat_message(message["role"], avatar="🦄"):
                st.write(message["content"])
        else:
            with st.chat_message(message["role"], avatar="🌍"):
                st.write(message["content"])

    # # # If last message is not from assistant, generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant", avatar="🌍"):
            with st.spinner("Thinking..."):
                # response = ask_rag(prompt, st.session_state.chat_engine)
                stream = st.session_state.chat_engine.stream(prompt)
                response = st.write_stream(stream)
                message = {"role": "assistant", "content": response}
                # Add response to message history
                st.session_state.messages.append(message)
                if message:
                    cloned_audio_save_path = speak(selected_name, response)
                    st.audio(cloned_audio_save_path)
