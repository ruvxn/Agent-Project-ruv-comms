import streamlit as st

from backend.model.states.GraphState import GraphState


def process_check_router(state: GraphState) -> GraphState:
    state = st.session_state.state
    if state.qa_state.is_processed:
        return "TRUE"
    else:
        return "FALSE"
