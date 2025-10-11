import copy
import json
import os
import tempfile
from dotenv import load_dotenv
import streamlit as st
from backend.model.states.GraphState import GraphState
from langchain_core.messages import HumanMessage, AIMessage
from backend.pipeline.get_graph import get_graph
from langsmith import traceable

from backend.pipeline.get_graph import get_graph

load_dotenv()

FILE_UPLOADER_PATH = os.getenv("FILE_UPLOADER_PATH")


@traceable
def render_main_section(state: GraphState) -> GraphState:
    st.title("PDF Agent")

    state = st.session_state.state
    render_file_uploader(state)

    if not getattr(state.messages, "message_placeholder", None):
        state.messages.message_placeholder = st.session_state.message_placeholder

    user_input = st.chat_input("Type Message")

    if user_input:
        state.messages.append(HumanMessage(content=user_input))
        placeholder = st.empty()
        placeholder.markdown("[AI is thinking...]")
        compiled_graph = get_graph(state)
        state_for_invoke = state.copy()
        state_for_invoke.qa_state = state.qa_state.dict()
        state_for_invoke.graph_config = state.graph_config.dict()
        compiled_graph.invoke(state_for_invoke)
        placeholder.markdown(" ")

    return state


def render_sidebar(state: GraphState) -> GraphState:
    with st.sidebar:
        log_tab, config_tab = st.tabs(["Logs", "Configs"])
        render_log_side_bar(state, log_tab)
        state = render_config_sidebar(state, config_tab)
    return state


def render_log_side_bar(state: GraphState, log_tab):
    with log_tab:
        if state.logs.log_placeholder is None:
            state.logs.log_placeholder = st.empty()

        # st.sidebar.markdown("[Chroma](http://localhost:8000/chroma)")
    from frontend.utils import render_log
    render_log(state.logs, state.logs.log_placeholder)


def render_config_sidebar(state: GraphState, config_tab) -> GraphState:
    with config_tab:
        st.subheader("Graph Config")

        if st.button("Reset Graph"):
            new_config = state.graph_config.copy(update={
                "CHUNK_SIZE": st.session_state["CHUNK_SIZE"],
                "CHUNK_OVERLAP": st.session_state["CHUNK_OVERLAP"],
                "TOP_K": st.session_state["TOP_K"],
                "RAG_THRESHOLD": st.session_state["RAG_THRESHOLD"],
                "SUMMARY_MIN_LENGTH": st.session_state["SUMMARY_MIN_LENGTH"],
                "SUMMARY_MAX_LENGTH": st.session_state["SUMMARY_MAX_LENGTH"],
                "SUMMARY_CHUNK_SIZE": st.session_state["SUMMARY_CHUNK_SIZE"],
                "SUMMARY_CHUNK_OVERLAP": st.session_state["SUMMARY_CHUNK_OVERLAP"],
                "SHOW_LOG": st.session_state["SHOW_LOG"]
            })
            st.session_state.state = GraphState(graph_config=new_config)
            st.session_state.state.logs.append("Graph has been reset.")
            if "file_uploader" in st.session_state:
                del st.session_state["file_uploader"]
            st.rerun()

        CHUNK_SIZE = st.number_input(
            "CHUNK_SIZE", key="CHUNK_SIZE", min_value=200, max_value=1000, value=state.graph_config.CHUNK_SIZE)
        CHUNK_OVERLAP = st.number_input(
            "CHUNK_OVERLAP", key="CHUNK_OVERLAP", min_value=50, max_value=150, value=state.graph_config.CHUNK_OVERLAP)
        RAG_THRESHOLD = st.number_input(
            "RAG_THRESHOLD", key="RAG_THRESHOLD", min_value=0.00, max_value=1.00, value=state.graph_config.RAG_THRESHOLD)
        TOP_K = st.number_input("TOP_K", key="TOP_K", min_value=1,
                                max_value=50, value=state.graph_config.TOP_K)
        SUMMARY_MIN_LENGTH = st.number_input(
            "SUMMARY_MIN_LENGTH", key="SUMMARY_MIN_LENGTH", min_value=500, max_value=800, value=state.graph_config.SUMMARY_MIN_LENGTH)
        SUMMARY_MAX_LENGTH = st.number_input(
            "SUMMARY_MAX_LENGTH", key="SUMMARY_MAX_LENGTH", min_value=800, max_value=1000, value=state.graph_config.SUMMARY_MAX_LENGTH)

        SUMMARY_CHUNK_SIZE = st.number_input(
            "SUMMARY_CHUNK_SIZE", key="SUMMARY_CHUNK_SIZE", min_value=100, max_value=5000, value=state.graph_config.SUMMARY_CHUNK_SIZE)
        SUMMARY_CHUNK_OVERLAP = st.number_input(
            "SUMMARY_CHUNK_OVERLAP", key="SUMMARY_CHUNK_OVERLAP", min_value=50, max_value=5000, value=state.graph_config.SUMMARY_CHUNK_OVERLAP)
        SHOW_LOG = st.checkbox("SHOW_LOG", True, key="SHOW_LOG")


def render_file_uploader(state: GraphState) -> GraphState:
    file_uploader = st.file_uploader(" ", type=[
                                     "pdf"], accept_multiple_files=[True], key="file_uploader")
    if file_uploader is not None:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(file_uploader.read())
            temp_file.flush()
            state.qa_state.pdf_path = temp_file.name
            state.qa_state.pdf_name = temp_file.name.split(".")[0]

        state.qa_state.is_upload = True
    else:
        state.qa_state.is_upload = False
        state.qa_state.is_processed = False

    state.logs.append(f"is_upload: {state.qa_state.is_upload}")
    return state


def render_chroma():
    return


def render_graph():
    graph.visualize()
    st.graphviz_chart(graph.get_graphviz())
