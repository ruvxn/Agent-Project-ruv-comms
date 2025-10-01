import asyncio
from dotenv import load_dotenv
from ollama import Tool, chat
from langchain_core.messages import AIMessage, HumanMessage
import os
import ollama
import streamlit
from backend.model.states.GraphState import GraphState
from backend.tools.chat_tool import chat_tool
from backend.tools.pdf_qa_tool import pdf_qa_tool
from backend.utils import get_user_input, log_decorator
from ollama import ChatResponse
import streamlit as st
from constants import SYSTEM_PROMPT_LIST
from backend.tools.get_tool_registry import get_tool_registry

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")


@log_decorator
async def tool_agent_async(state: GraphState) -> GraphState:
    user_input = get_user_input()
    is_upload = state.pdf.is_upload
    state.logs.append(f"testtttttt:{is_upload}")
    client = ollama.AsyncClient()
    system_prompt = SYSTEM_PROMPT_LIST.tool_router_prompt.format(
        user_input=user_input, is_upload=is_upload)

    state.logs.append(f"{system_prompt}")

    if not user_input:
        return state

    response = await client.chat(
        OLLAMA_MODEL,
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": user_input}],
        tools=[pdf_qa_tool, chat_tool],
    )

    state.logs.append(f"{response}")

    if not response.message.tool_calls:
        return state

    tool_call = response.message.tool_calls[0]
    tool_name = tool_call.function.name
    args = tool_call.function.arguments or {}
    args["state"] = state
    tool_registry = get_tool_registry()
    tool = tool_registry[tool_name]
    result = tool.invoke({"state": state, **args})
    state = result.state
    return state


@log_decorator
def tool_agent(state: GraphState) -> GraphState:
    state = st.session_state.state
    return asyncio.run(tool_agent_async(state))
