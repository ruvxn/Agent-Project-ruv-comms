import json
import streamlit as st
from backend.model.states.GraphState import GraphState
from langchain_core.messages import HumanMessage, AIMessage
from backend.pipeline.workflow import get_graph
from langsmith import traceable


@traceable
def render_main_section(state: GraphState) -> GraphState:
    st.title("PDF Agent")
    state = st.session_state.state

    if not getattr(state.messages, "message_placeholder", None):
        state.messages.message_placeholder = st.session_state.message_placeholder

    user_input = st.chat_input("Type Message")

    if user_input:
        state.messages.append(HumanMessage(content=user_input))
        placeholder = st.empty()
        placeholder.markdown("AI is thinking...")
        compiled_graph = get_graph(state)
        compiled_graph.invoke(json.loads(state.json()))

        placeholder.markdown(" ")

    return state


def render_side_bar(state: GraphState) -> GraphState:
    st.sidebar.title("Processor Logs")
    # st.sidebar.markdown("[Chroma](http://localhost:8000/chroma)")
    if not getattr(state.logs, "log_placeholder", None):
        state.logs.log_placeholder = st.session_state.log_placeholder
    return state


def render_chroma():
    return


def render_graph():
    graph.visualize()
    st.graphviz_chart(graph.get_graphviz())
