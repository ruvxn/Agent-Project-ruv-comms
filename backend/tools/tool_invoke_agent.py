import asyncio
import json
from dotenv import load_dotenv
from ollama import Tool, chat
from langchain_core.messages import AIMessage, HumanMessage
import os
import ollama
import streamlit
from backend.model.states.GraphState import GraphState
from backend.tools.fei_tool.chat_tool import chat_tool
from backend.tools.fei_tool.qa_tool import qa_tool
from backend.tools.fei_tool.summary_tool import summary_tool
from backend.utils import get_user_input, log_decorator
from ollama import ChatResponse
import streamlit as st
from constants import SYSTEM_PROMPT_LIST
from backend.tools.get_tool_registry import get_tool_registry

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")


@log_decorator
async def tool_agent_async(state: GraphState) -> GraphState:
    client = ollama.AsyncClient()
    user_input = get_user_input()
    bind_tools = get_bind_tools(state)

    system_prompt = SYSTEM_PROMPT_LIST.tool_router_prompt.format(
        user_input=user_input, tool_names={bind_tool["name"] for bind_tool in bind_tools})

    if not user_input:
        return state

    response = await client.chat(
        OLLAMA_MODEL,
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": user_input}],
        tools=[bind_tool["tool"] for bind_tool in bind_tools],
    )

    state.logs.append(f"{response}")

    if response.message.content:
        if response.message.content:
            import ast
            try:
                content_json = json.loads(response.message.content)
            except json.JSONDecodeError:
                content_json = ast.literal_eval(response.message.content)

    return invoke_tool(response.message, bind_tools, state)


@log_decorator
def tool_agent(state: GraphState) -> GraphState:
    state = st.session_state.state
    return asyncio.run(tool_agent_async(state))


@log_decorator
def get_bind_tools(state: GraphState) -> list:
    tool_to_bind = []
    tool_registry = get_tool_registry()
    user_input = get_user_input()

    for tool_info in tool_registry.values():
        if tool_info["condition"](state, user_input):
            tool_to_bind.append(tool_info)

    tool_to_bind.sort(key=lambda t: t["priority"])

    state.logs.append(
        f"bind_tools: {[bind_tool['name'] for bind_tool in tool_to_bind]}")

    return tool_to_bind


@log_decorator
def invoke_tool(message, bind_tools, state: GraphState) -> GraphState:
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        tool_name = tool_call.function.name
        args = tool_call.function.arguments or {}
    else:
        try:
            content_json = json.loads(message.content)
        except json.JSONDecodeError:
            fixed_content = message.content.replace("'", '"')
            content_json = json.loads(fixed_content)

        tool_name = content_json["tool_name"] if content_json["tool_name"] else content_json["tool"]
        args = content_json.get("args", {})

    args["state"] = state

    tool_to_invoke = next(
        bind_tool for bind_tool in bind_tools if bind_tool["name"] == tool_name)

    result = tool_to_invoke["invoke"].invoke(args)
    return result.state
