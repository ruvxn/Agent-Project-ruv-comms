from dotenv import load_dotenv
from ollama import chat
from langchain_core.messages import AIMessage, HumanMessage
import os

import streamlit

from backend.model.states.GraphState import GraphState
from backend.utils import log_decorator

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")


@log_decorator
def chat_agent(state: GraphState) -> GraphState:
    state = streamlit.session_state.state
    user_input = state.messages.user_query_list[-1].content if len(
        state.messages.user_query_list) > 0 else None
    if user_input:
        state.messages.append(HumanMessage(content=user_input))

        response = chat(
            OLLAMA_MODEL, [{"role": "user", "content": user_input}])

        print(response)
        state.messages.append(AIMessage(content=response.message.content))

    return state
