import json
import os
import tempfile
from dotenv import load_dotenv
import streamlit as st
from backend.model.states.GraphState import GraphState
from langchain_core.messages import HumanMessage, AIMessage
from backend.pipeline.workflow import get_graph
from langsmith import traceable

load_dotenv()

FILE_UPLOADER_PATH = os.getenv("FILE_UPLOADER_PATH")


@traceable
def render_main_section(state: GraphState) -> GraphState:
    st.title("PDF Agent")
    render_file_uploader(state)
    state = st.session_state.state

    if not getattr(state.messages, "message_placeholder", None):
        state.messages.message_placeholder = st.session_state.message_placeholder

    user_input = st.chat_input("Type Message")

    if user_input:
        state.messages.append(HumanMessage(content=user_input))
        placeholder = st.empty()
        placeholder.markdown("[AI is thinking...]")
        compiled_graph = get_graph(state)
        state_for_invoke = state.copy()
        state_for_invoke.pdf = state.pdf.dict()
        compiled_graph.invoke(state_for_invoke, config={
            "configurable": {"thread_id": "abc123"}})
        placeholder.markdown(" ")

    return state


def render_side_bar(state: GraphState) -> GraphState:
    st.sidebar.title("Processor Logs")
    # st.sidebar.markdown("[Chroma](http://localhost:8000/chroma)")
    if not getattr(state.logs, "log_placeholder", None):
        state.logs.log_placeholder = st.session_state.log_placeholder
    return state


def render_file_uploader(state: GraphState) -> GraphState:
    state = st.session_state.state
    file_uploader = st.file_uploader(" ", type=[
                                     "pdf"], accept_multiple_files=[True])
    if file_uploader is not None:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(file_uploader.read())
            temp_file.flush()
            state.pdf.pdf_path = temp_file.name
            state.pdf.pdf_name = temp_file.name.split(".")[0]

        state.logs.append(f"get pdf_path: {state.pdf.pdf_path}")
        state.logs.append(f"get pdf_name: {state.pdf.pdf_name}")

        state.pdf.is_upload = True
    return state


def render_chroma():
    return


def render_graph():
    graph.visualize()
    st.graphviz_chart(graph.get_graphviz())
