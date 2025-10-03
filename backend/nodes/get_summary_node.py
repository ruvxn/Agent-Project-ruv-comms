import os
import dotenv
import streamlit
from backend.embedding.chroma_setup import insert_pdf_summary
from backend.model.states.GraphState import GraphState
from backend.utils import single_chunk_summary, clean_text, log_decorator

dotenv.load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")


@log_decorator
def get_summary_node(state: GraphState) -> GraphState:
    summaries = []
    state = streamlit.session_state.state

    for single_page_pdf_text in state.qa_state.chunked_pdf_text:
        summaries.append(single_chunk_summary(
            clean_text(single_page_pdf_text.chunk)))

    if summaries:
        summaries_string = " ".join(summaries)
        state.qa_state.final_summary = single_chunk_summary(summaries_string)
        insert_pdf_summary(state)
    else:
        state.qa_state.final_summary = "No content to summarize."

    return state
