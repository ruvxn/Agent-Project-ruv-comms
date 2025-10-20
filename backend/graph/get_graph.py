import os
import sqlite3
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from backend.embedding.sql_setup import create_checkpoint_memory
from backend.model.states.graph_state.GraphState import GraphState
from backend.tools.tool_invoke_agent import tool_agent
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class State(TypedDict):
    """An agent state"""
    messages: Annotated[list, add_messages]
    plan: str
    critique: str

async def get_graph(state: GraphState) -> StateGraph:

    graph = StateGraph(GraphState)

    graph.add_node("tool_agent", tool_agent)

    graph.add_edge(START, "tool_agent")
    graph.add_edge("tool_agent", END)

    memory = create_checkpoint_memory()

    return graph.compile()
