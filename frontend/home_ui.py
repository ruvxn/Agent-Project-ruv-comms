import copy
import json
import os
import tempfile
from dotenv import load_dotenv
import streamlit as st
from backend.model.states.StateManager import StateManager
from backend.model.states.graph_state.GraphState import GraphState
from langchain_core.messages import HumanMessage, AIMessage
from backend.graph.get_graph import get_graph
from langsmith import traceable
from langgraph.checkpoint.sqlite import SqliteSaver
from nicegui import ui, app, events
load_dotenv()

#SQL_PATH = os.getenv("SQL_PATH")

#FILE_UPLOADER_PATH = os.getenv("FILE_UPLOADER_PATH")


@traceable
@ui.page("/")
def render_main_section(state: GraphState) -> GraphState:
    async def handle_submit():
        text_to_send = user_input.value
        if not text_to_send:
            return
        state.messages.append(HumanMessage(
            content=text_to_send), True)
        StateManager.update_state(state)

        compiled_graph = await get_graph(state)
        state_for_invoke = state
        new_state = await compiled_graph.ainvoke(state_for_invoke, config={
            "thread_id": "123"})
        print(new_state)
        StateManager.update_state(new_state)
        if isinstance(new_state, dict):
            new_state = GraphState(**new_state)

    async def handle_upload(e: events.UploadEventArguments):
        try:
            content = await e.file.text()
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_file.write(content)
                temp_file.flush()
                state.qa_state.pdf_path = temp_file.name
                state.qa_state.pdf_name = e.file.name
                print(state.qa_state.is_upload)
                print(state.qa_state.pdf_path)
                print(state.qa_state.pdf_name)
        except Exception as e:
            print("Error", e)
        state.qa_state.is_upload = True

    def handle_multiple_upload(e: events.MultiUploadEventArguments):
        try:
            for files in e.files:
                e.content.seek(0)
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                    temp_file.write(e.content.read().decode('utf-8'))
                    temp_file.flush()
                    state.qa_state.pdf_path = temp_file.name
                    state.qa_state.pdf_name = e.name
        except Exception as e:
            return ("Failed")
        state.qa_state.is_upload = True

    ui.upload(
        on_upload=handle_upload,
        #on_multi_upload=handle_multiple_upload,
        multiple=False,
        auto_upload=False,
        label='Upload File',
    ).props('accept=".pdf"')

    with ui.column().classes('w-full items-center'):
        ui.label('Welcome').classes('text-2xl mt-4')
    chat_container = ui.column().classes('w-full max-w-2xl mx-auto gap-4 p-4')


    with ui.footer().classes('bg-white'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        with ui.row().classes('w-full no-wrap items-center'):
            user_input = ui.input(placeholder="Ask Agent...") \
                .classes('flex-grow').on('keydown.enter', handle_submit)
            submit_button = ui.button('>', on_click=handle_submit)
            submit_button.bind_enabled_from(user_input, 'value')


        def update_chat_display():
            chat_container.clear()






"""
 if not getattr(state.messages, "message_placeholder", None):
        state.messages.message_placeholder = st.session_state.message_placeholder

    if "initialized" not in st.session_state:

        with SqliteSaver.from_conn_string("db/test.db") as checkpointer:
            checkpoint_data = checkpointer.get(
                {"configurable": {"thread_id": "123"}})

        if checkpoint_data:
            fake_msg = AIMessage(
                content="*****[Restored previous messages]*****")
            state.messages.append(fake_msg, True)

        st.session_state.initialized = True
       
def render_sidebar(state: GraphState) -> GraphState:
    with st.sidebar:
        log_tab, config_tab = st.tabs(["Logs", "Configs"])
        render_log_side_bar(state, log_tab)
        render_config_sidebar(state, config_tab)
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
            new_state = GraphState(graph_config=new_config)
            new_state.logs.append("Graph has been reset.")
            StateManager.update_state(new_state)
            if "file_uploader" in st.session_state:
                del st.session_state["file_uploader"]
            st.rerun()

        SEARCH_ALL_COLLECTION = st.checkbox(
            "SEARCH_ALL_COLLECTION", False, key="SEARCH_ALL_COLLECTION")
        CHUNK_SIZE = st.number_input(
            "CHUNK_SIZE", key="CHUNK_SIZE", min_value=200, max_value=1000, value=state.graph_config.CHUNK_SIZE)
        CHUNK_OVERLAP = st.number_input(
            "CHUNK_OVERLAP", key="CHUNK_OVERLAP", min_value=50, max_value=150, value=state.graph_config.CHUNK_OVERLAP)
        RAG_THRESHOLD = st.number_input(
            "RAG_THRESHOLD", key="RAG_THRESHOLD", min_value=0.00, max_value=1.00, value=state.graph_config.RAG_THRESHOLD)
        TOP_K = st.number_input("TOP_K", key="TOP_K", min_value=1,
                                max_value=50, value=state.graph_config.TOP_K)
        SUMMARY_MIN_LENGTH = st.number_input(
            "SUMMARY_MIN_LENGTH", key="SUMMARY_MIN_LENGTH", min_value=500, max_value=1500, value=state.graph_config.SUMMARY_MIN_LENGTH)
        SUMMARY_MAX_LENGTH = st.number_input(
            "SUMMARY_MAX_LENGTH", key="SUMMARY_MAX_LENGTH", min_value=800, max_value=2000, value=state.graph_config.SUMMARY_MAX_LENGTH)

        SUMMARY_CHUNK_SIZE = st.number_input(
            "SUMMARY_CHUNK_SIZE", key="SUMMARY_CHUNK_SIZE", min_value=100, max_value=5000, value=state.graph_config.SUMMARY_CHUNK_SIZE)
        SUMMARY_CHUNK_OVERLAP = st.number_input(
            "SUMMARY_CHUNK_OVERLAP", key="SUMMARY_CHUNK_OVERLAP", min_value=50, max_value=5000, value=state.graph_config.SUMMARY_CHUNK_OVERLAP)
        SHOW_LOG = st.checkbox("SHOW_LOG", True, key="SHOW_LOG")

 """
def render_file_uploader(state: GraphState) -> GraphState:
    def handle_upload(e: events.UploadEventArguments):
        try:
            e.content.seek(0)
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_file.write(e.content.read().decode('utf-8'))
                temp_file.flush()
                state.qa_state.pdf_path = temp_file.name
                state.qa_state.pdf_name = e.name
                print(state.qa_state.is_upload)
                print(state.qa_state.pdf_path)
                print(state.qa_state.pdf_name)
        except Exception as e:
            return ("Failed")
        state.qa_state.is_upload = True
    def handle_multiple_upload(e: events.MultiUploadEventArguments):
            try:
                for files in e.files:
                    e.content.seek(0)
                    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                        temp_file.write(e.content.read().decode('utf-8'))
                        temp_file.flush()
                        state.qa_state.pdf_path = temp_file.name
                        state.qa_state.pdf_name = e.name
            except Exception as e:
                return ("Failed")
            state.qa_state.is_upload = True

    ui.upload(
        on_upload=handle_upload,
        on_multi_upload=handle_multiple_upload,
        auto_upload=True,
        label='Upload Text',
    ).props('accept=".pdf"')


    return state


