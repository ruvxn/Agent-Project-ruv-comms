import os
from dotenv import load_dotenv
from backend.model.states.GraphState import GraphState
import streamlit as st
from ollama import chat
from langchain_core.messages import AIMessage

from backend.utils import log_decorator
load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")


@log_decorator
def rag_agent(state: GraphState) -> GraphState:
    state = st.session_state.state

    user_input = state.messages.user_query_list[-1].content if len(
        state.messages.user_query_list) > 0 else state.logs.append(f"[rag_agent] call return; user_input is None")

    prompt = state.messages.system_message_list.top_k_kb_found_prompt.format(
        user_input=user_input,
        top_k_kb=state.pdf.top_k_kb)

    if user_input:
        response = chat(
            OLLAMA_MODEL, [{"role": "system", "content":
                            prompt}, {"role": "user", "content": user_input}])

    state.messages.append(
        AIMessage(content=response.message.content))
    state.logs.append(f"[rag_agent] prompt: {prompt}")
    return state
