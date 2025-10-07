from dotenv import load_dotenv
from ollama import chat
from langchain_core.messages import AIMessage, HumanMessage
import os
import streamlit as st
from mainagent.backend.model.states.GraphState import GraphState
from mainagent.backend.utils import get_user_input, log_decorator

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")


@log_decorator
def chat_agent(state: GraphState) -> GraphState:
    state = st.session_state.state

    user_input = get_user_input()

    system_prompt = "You are an assistant."
    if getattr(state.qa_state, "final_summary", None):
        system_prompt += f"\nReference PDF Summary:\n{state.qa_state.final_summary}"

    if user_input:
        response = chat(
            OLLAMA_MODEL, [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}])

        state.logs.append(system_prompt)
        state.logs.append(response)
        state.messages.append(AIMessage(content=response.message.content))

    return state
