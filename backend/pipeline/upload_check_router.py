import streamlit as st

from backend.model.states.GraphState import GraphState


def upload_check_router(state: GraphState) -> GraphState:
    state = st.session_state.state
    if state.pdf.is_upload:
        state.pdf.is_upload = False
        return "TRUE"
    else:
        return "FALSE"
