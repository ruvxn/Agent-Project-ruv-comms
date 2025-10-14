import os
from dotenv import load_dotenv
from backend.model.states.graph_state.GraphState import GraphState
import streamlit as st
from ollama import chat
from langchain_core.messages import AIMessage

from backend.utils import get_user_input, log_decorator
load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")


def rag_agent(state: GraphState) -> GraphState:
    user_input = get_user_input()

    prompt = state.messages.system_message_list.top_k_kb_found_prompt.format(
        user_input=user_input,
        top_k_kb=state.qa_state.top_k_kb)

    if user_input:
        response = chat(
            OLLAMA_MODEL, [{"role": "system", "content":
                            prompt}, {"role": "user", "content": user_input}])

    state.messages.append(
        AIMessage(content=response.message.content))
    state.logs.append(f"[rag_agent] prompt: {prompt}")
    return state
