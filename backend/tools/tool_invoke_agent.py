import asyncio
import json
import re
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
import os
import ollama
from backend.model.states.graph_state.GraphState import GraphState
from backend.tools.command import command
from backend.utils import get_user_input, log_decorator
import streamlit as st
from constants import SYSTEM_PROMPT_LIST
from backend.tools.get_tool_registry import get_tool_registry

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")


async def tool_agent_async(state: GraphState) -> GraphState:
    client = ollama.AsyncClient()
    user_input = get_user_input()

    bind_tools = get_bind_tools(state)

    system_prompt = SYSTEM_PROMPT_LIST.tool_router_prompt.format(
        user_input=user_input, tool_names={bind_tool["name"] for bind_tool in bind_tools} or "none")

    response = await client.chat(
        OLLAMA_MODEL,
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": user_input}],
        tools=[bind_tool["tool"] for bind_tool in bind_tools],
    )

    state.logs.append(f"{response}")

    final_state = invoke_tool(response.message, bind_tools, state)
    return final_state


@log_decorator
def tool_agent(state: GraphState) -> GraphState:
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
    tool_name_args = get_tool_name_list(message, state)

    for tool_name, args in tool_name_args:
        tool_to_invoke = next(
            bind_tool for bind_tool in bind_tools if bind_tool["name"] == tool_name)

        result = tool_to_invoke["invoke"].invoke(args)
        new_state = command(tool_name, result)
    return new_state


def get_tool_name_list(message, state: GraphState) -> list[tuple[str, dict]]:
    tool_name_args = []
    if message.tool_calls:
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            args = tool_call.function.arguments or {}
            args["state"] = state
            tool_name_args.append((tool_name, args))
    else:
        try:
            try:
                content_json = json.loads(message.content)
            except json.JSONDecodeError:
                fixed_content = message.content.replace("'", '"')
                content_json = json.loads(fixed_content)

            tools = content_json.get("tools", [])
            for t in tools:
                tool_name = t.get("tool_name") or t.get("tool")
                if not tool_name:
                    continue
                args = t.get("args", {})
                args["state"] = state
                tool_name_args.append((tool_name, args))
        except:
            state.messages.ai_response_list.append(
                AIMessage(content="Can I Beg Your Pardon?"))

    return tool_name_args
