import os
from dotenv import load_dotenv
import streamlit
from mainagent.backend.model.states.GraphState import GraphState
from ollama import chat
from langchain_core.messages import AIMessage

from mainagent.backend.utils import log_decorator

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")


@log_decorator
def no_kb_agent(state: GraphState) -> GraphState:
    state = streamlit.session_state.state
    system_input = state.messages.system_message_list.top_k_kb_not_found_prompt
    response = chat(
        OLLAMA_MODEL, [{"role": "system", "content": system_input}, {"role": "user", "content": "Please out put kb not found"}])
    state.messages.append(AIMessage(
        content=response.message.content))
    return state
