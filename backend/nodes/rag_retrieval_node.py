from typing import List
import os
from dotenv import load_dotenv
import streamlit
from backend.model.states.GraphState import GraphState
from backend.model.states.PdfTextClass import Meta, PdfTextClass

from backend.utils import get_embedding, log_decorator

load_dotenv()

EMBED_MODEL = os.getenv("EMBED_MODEL")
TOP_K = int(os.getenv("TOP_K", "5"))


@log_decorator
def rag_retrieval_node(state: GraphState, collection, embeded_query) -> tuple[str, list[float]]:
    state = streamlit.session_state.state

    try:
        result = collection.query(
            query_embeddings=embeded_query, n_results=TOP_K, include=["distances"])
    except Exception:
        return "", 0

    if result:
        top_k_result = top_k_result_to_log(state, result)
        top_k_kb = "\n".join([pdf_text.chunk for pdf_text in top_k_result])
        top_k_scores = [1 - d for d in result['distances'][0]]
        top_k_avg_score = sum(top_k_scores) / \
            len(top_k_scores) if top_k_scores else 0
    else:
        top_k_kb = None
        top_k_avg_score = 0
    return top_k_kb, top_k_avg_score


def top_k_result_to_log(state, query) -> List[PdfTextClass]:
    state = streamlit.session_state.state

    top_k_result: List[PdfTextClass] = []
    for doc_list, meta_list in zip(query.get('documents', []), query.get('metadatas', [])):
        for doc, meta in zip(doc_list, meta_list):
            pdf_text_obj = PdfTextClass(
                chunk=doc,
                meta=Meta(**meta)
            )
            top_k_result.append(pdf_text_obj)
        state.logs.append(
            f"[TOP_{TOP_K}_RESULT] pdf_name: {pdf_text_obj.meta.pdf_name}, "
            f"page_number: {pdf_text_obj.meta.page_number}, "
            f"chunk_summary: {pdf_text_obj.meta.chunk_summary}"
        )
    return top_k_result
