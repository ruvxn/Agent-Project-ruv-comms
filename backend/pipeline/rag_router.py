import os
from dotenv import load_dotenv
import streamlit
from backend.embedding.chroma_setup import get_or_create_summary_collection
from backend.model.states.GraphState import GraphState
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from backend.nodes.rag_retrieval_node import rag_retrieval_node

from backend.utils import get_embedding, log_decorator


load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
TOP_K = int(os.getenv("TOP_K", "5"))
RAG_THRESHOLD = float(os.getenv("RAG_THRESHOLD", "0.7"))


@log_decorator
def rag_router(state: GraphState) -> GraphState:
    """Decide whether should use rag"""
    state = streamlit.session_state.state

    collection = get_or_create_summary_collection()

    if not collection:
        state.logs.append(
            "[rag_router] No PDF_SUMMARY_COLLECTION collection found, should_use_rag == FALSE")
        return "FALSE"

    user_input = (
        state.messages.user_query_list[-1].content
        if state.messages.user_query_list else None
    )

    if user_input:
        embed_user_input = get_embedding([user_input])
        top_k_kb, top_k_avg_score = rag_retrieval_node(
            state, collection, embed_user_input)
    else:
        state.logs.append(
            "[rag_router] No user_input, should_use_rag == FALSE")
        return "FALSE"

    should_use_rag = (top_k_avg_score >= RAG_THRESHOLD)

    if should_use_rag and top_k_kb:
        state.pdf.top_k_kb = top_k_kb

    state.logs.append(
        f"{rag_router.__name__} decide should_use_rag == '{should_use_rag}' top_k_avg_score: {top_k_avg_score}; rag_threshold: {RAG_THRESHOLD}")

    return "TRUE"
