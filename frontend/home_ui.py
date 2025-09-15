import streamlit as st
from backend.embedding.chroma_setup import insert_into_chroma
from backend.model.data_class.PipelineState import PipelineState
from backend.nodes.chat_agent import chat_agent
from backend.nodes.extract_pdf_to_chunk import extract_pdf_to_chunk
from backend.nodes.get_pdf_summary import get_pdf_summary
from langchain_core.messages import HumanMessage, AIMessage


def render_main_section(state: PipelineState) -> PipelineState:
    st.title("PDF Agent")
    # uploaded_file = st.file_uploader("Upload pdf", type="pdf")

    if "history" not in st.session_state:
        st.session_state.history = []

    user_input = st.chat_input("Type Message")

    if user_input:
        st.session_state.history.append(("user", user_input))
        state.messages.append(HumanMessage(content=user_input))

        placeholder = st.empty()
        placeholder.markdown("AI is thinking...")

        agent_response = chat_agent("User", user_input)

        st.session_state.history.append(("agent", agent_response))
        state.messages.append(AIMessage(content=agent_response))

        placeholder.markdown(" ")

        if st.session_state.history:
            for role, history in st.session_state.history:
                st.write(f"{role}: {history}")

    return state


def render_side_bar(state: PipelineState) -> PipelineState:
    st.sidebar.title("Plugin")
    st.sidebar.markdown("[Chroma](http://localhost:8000/chroma)")
    state.use_rag = st.sidebar.toggle("use RGV?")
    return state


def render_chroma():
    return


def render_graph():
    graph.visualize()
    st.graphviz_chart(graph.get_graphviz())


def render_log(state: PipelineState) -> PipelineState:
    message_container = st.empty()
    for node in [extract_pdf_to_chunk, get_pdf_summary, insert_into_chroma]:
        state = node(state)
        message_container.text("\n".join(state.message))
    return state
