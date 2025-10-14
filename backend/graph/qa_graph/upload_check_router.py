import streamlit as st

from backend.model.states.graph_state.GraphState import GraphState


def upload_check_router(state: GraphState) -> str:
    if state.qa_state.is_upload:
        return "TRUE"
    else:
        return "FALSE"
