from dotenv import load_dotenv
import os
import streamlit as st
from backend.model.states.GraphState import GraphState
from backend.model.stores.LogStore import LogStore
from backend.model.stores.MessageStore import MessageStore
from backend.pipeline.workflow import get_graph
from frontend.home_ui import render_main_section, render_side_bar


load_dotenv()
PDF_PATH = os.getenv("PDF_PATH")
PDF_NAME = os.getenv("PDF_NAME")


def start():
    if "state" not in st.session_state:
        st.session_state.state = GraphState()

    state = st.session_state.state
    state.pdf.pdf_path = PDF_PATH

    if "log_placeholder" not in st.session_state:
        st.session_state.log_placeholder = st.sidebar.empty()

    if "message_placeholder" not in st.session_state:
        st.session_state.message_placeholder = st.empty()

    render_side_bar(state)
    render_main_section(state)


start()
