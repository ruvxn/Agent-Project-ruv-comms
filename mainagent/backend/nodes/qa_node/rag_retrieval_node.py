from typing import List
import os
from dotenv import load_dotenv
import streamlit
from mainagent.backend.model.states.GraphState import GraphState
from mainagent.backend.model.states.qa_state.PdfTextClass import Meta, PdfTextClass


from mainagent.backend.utils import get_embedding, log_decorator

load_dotenv()

EMBED_MODEL = os.getenv("EMBED_MODEL")


@log_decorator
def rag_retrieval_node(state: GraphState, collection, embeded_query) -> tuple[str, list[float]]:
    state = streamlit.session_state.state

    try:
        num = collection.count()
        result = collection.query(
            query_embeddings=embeded_query, n_results=state.graph_config.TOP_K, include=["documents", "distances", "metadatas"])
    except Exception:
        return None, 0.0

    if result.get("documents"):
        top_k_result = top_k_result_to_log(state, result)
        top_k_kb = "\n".join([pdf_text.chunk for pdf_text in top_k_result])
        top_k_scores = [1 - d for d in result['distances'][0]]
        top_score = max(top_k_scores)

        # top_3_avg_score = sum(sorted(top_k_scores, reverse=True)
        #                       [:3])/min(3, len(top_k_scores))
    else:
        top_k_kb = None
        top_score = 0.0
    return top_k_kb, top_score


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
                f"[TOP_{state.graph_config.TOP_K}_RESULT] pdf_name: {pdf_text_obj.meta.pdf_name}, "
                f"page_number: {pdf_text_obj.meta.page_number}, "
                # f"chunk_summary: {pdf_text_obj.meta.chunk_summary}"
                f"chunk_content: {pdf_text_obj.chunk}"
            )
    return top_k_result
