from backend.embedding.chroma_setup import insert_chunks
from backend.model.states.GraphState import GraphState
from backend.nodes.chunk_pdf_node import chunk_pdf_node
from backend.nodes.embed_pdf_node import embed_pdf_node
from backend.nodes.get_summary_node import get_summary_node
from backend.utils import log_decorator
import streamlit as st


@log_decorator
def get_pdf_ready_pipeline(state: GraphState) -> GraphState:
    """
    Pipeline to process an uploaded PDF:
    1. Extract chunks
    2. Embed each chunk
    3. Insert chunk to chroma
    4. Get summaries as meta
    5. insert summaries to chroma
    """

    if getattr(state.pdf, "is_upload") and not getattr(state.pdf, "is_processed"):
        chunk_pdf_node(state)
        embed_pdf_node(state)
        insert_chunks(state)
        # get_summary_node(state)

        st.session_state.state.pdf.is_processed = True
    return state
