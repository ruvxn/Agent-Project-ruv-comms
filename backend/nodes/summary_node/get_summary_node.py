import copy
import os
from dotenv import load_dotenv
import streamlit
from backend.embedding.chroma_setup import insert_pdf_summary
from backend.model.states.GraphState import GraphState
from backend.utils import single_chunk_summary, clean_text, log_decorator

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")


@log_decorator
def get_summary_node(state: GraphState) -> GraphState:
    if state.summary_state.final_summary:
        return state

    chunked_text_content = [
        copy.deepcopy(chunk.chunk) for chunk in state.qa_state.chunked_pdf_text
    ]

    for idx, chunk_content in enumerate(chunked_text_content, start=1):
        state.logs.append(
            f"[Summary Node] Processing chunk {idx}/{len(chunked_text_content)}"
        )
        clean_chunk = clean_text(chunk_content)
        chunk_summary = single_chunk_summary(clean_chunk)
        state.summary_state.chunk_summary.append(chunk_summary)

    if state.summary_state.chunk_summary:
        summaries_string = " ".join(state.summary_state.chunk_summary)
        state.summary_state.final_summary = single_chunk_summary(
            summaries_string, state.graph_config.SUMMARY_MIN_LENGTH, state.graph_config.SUMMARY_MAX_LENGTH)

        insert_pdf_summary(state)
    else:
        state.summary_state.final_summary = "No content to summarize."

    return state
