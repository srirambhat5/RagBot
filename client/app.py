import uuid
import streamlit as st

from components.upload import render_uploader
from components.chatUI import render_chat
from components.history_download import render_history_download


st.set_page_config(
    page_title="RAGBot 2.0",
    layout="wide"
)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


st.title("RAG PDF Chatbot")

render_uploader()
render_chat()
render_history_download()