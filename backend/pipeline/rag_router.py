import os
from dotenv import load_dotenv
import streamlit
from backend.embedding.chroma_setup import get_all_collection_name, get_collection, get_or_create_summary_collection
from backend.model.states.GraphState import GraphState
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from backend.nodes.rag_retrieval_node import rag_retrieval_node
from backend.pipeline.get_pdf_ready_pipeline import get_pdf_ready_pipeline

from backend.utils import get_embedding, get_user_input, log_decorator


load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
PDF_SUMMARY_COLLECTION = os.getenv("PDF_SUMMARY_COLLECTION")


@log_decorator
def rag_router(state: GraphState) -> str:
    """Decide whether should use rag"""

    state = streamlit.session_state.state
    log_template = state.logs.system_log_list.rag_router_log_template

    user_input = get_user_input()
    if not user_input:
        state.logs.append(log_template.no_user_input_error)
        return "FALSE"

    try:
        get_all_collection_name(state)

        for collection_name in state.collection_names_list:
            collection = get_collection(collection_name)
            state.messages.append(state.collection_names_list)
            if collection:
                if collection.count() == 0:
                    state.logs.append(
                        log_template.empty_collection_error)
                    continue
                try:
                    embed_user_input = get_embedding([user_input])
                    top_k_kb, top_score = rag_retrieval_node(
                        state, collection, embed_user_input)
                except Exception as e:
                    state.logs.append(
                        log_template.rag_retrieval_exception.format(e=e))
                    return "FALSE"
                if top_k_kb and top_score >= state.graph_config.RAG_THRESHOLD:
                    state.pdf.top_k_kb = top_k_kb
                    state.logs.append(log_template.successful_log.format(
                        top_score=top_score, RAG_THRESHOLD=state.graph_config.RAG_THRESHOLD))
                    return "TRUE"
                else:
                    continue
            else:
                return "FALSE"
    except Exception as e:
        state.logs.append(
            log_template.get_collection_exception.format(e=e))
        return "FALSE"

    if top_score <= 0:
        state.logs.append(
            log_template.chat_agent_log.format(top_score=top_score))
        return "FALSE"

    state.logs.append(log_template.no_kb_log.format(
        top_score=top_score, RAG_THRESHOLD=state.graph_config.RAG_THRESHOLD))
    return "NO_KB"
