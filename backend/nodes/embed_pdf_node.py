
import streamlit
from backend.model.states.GraphState import GraphState
from backend.utils import get_embedding


def embed_pdf_node(state: GraphState):
    state = streamlit.session_state.state
    if state.pdf.chunked_pdf_text is None:
        state.logs.append("No chunk found, skipping.")
        return state

    chunked_pdf_text = state.pdf.chunked_pdf_text
    texts = [pdf_text.chunk for pdf_text in chunked_pdf_text]

    embedding = get_embedding(texts)
    total_chunk = len(state.pdf.chunked_pdf_text)

    for i, pdf_text in enumerate(state.pdf.chunked_pdf_text):
        pdf_text.embedding = embedding[i]

        state.logs.append(
            f"Generate {i+1}/{total_chunk} chunk.")

    return state
