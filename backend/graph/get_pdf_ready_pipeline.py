from backend.model.states.graph_state.GraphState import GraphState
from backend.nodes.pdf_node.chunk_pdf_node import chunk_pdf_node
from backend.utils import log_decorator
import streamlit as st


@log_decorator
def get_pdf_ready_pipeline(state: GraphState) -> GraphState:
    if getattr(state.qa_state, "is_upload") and not getattr(state.qa_state, "is_processed"):
        chunk_pdf_node(state)
        state.qa_state.is_processed = True
    return state
