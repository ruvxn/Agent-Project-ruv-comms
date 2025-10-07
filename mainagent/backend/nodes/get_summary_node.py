import os
import dotenv
import streamlit
from mainagent.backend.embedding.chroma_setup import insert_pdf_summary
from mainagent.backend.model.states.GraphState import GraphState
from mainagent.backend.utils import single_chunk_summary, clean_text, log_decorator

dotenv.load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")


@log_decorator
def get_summary_node(state: GraphState) -> GraphState:
    summaries = []

    if state.qa_state.final_summary:
        return

    for count, single_page_pdf_text in enumerate(state.qa_state.chunked_pdf_text, start=1):
        state.logs.append(
            f"[Summary Node] {count}/{len(state.qa_state.chunked_pdf_text)} chunk summary generated."
        )
        summaries.append(single_chunk_summary(
            clean_text(single_page_pdf_text.chunk)))

    if summaries:
        summaries_string = " ".join(summaries)
        state.qa_state.final_summary = single_chunk_summary(summaries_string)
        insert_pdf_summary(state)
    else:
        state.qa_state.final_summary = "No content to summarize."

    return state
