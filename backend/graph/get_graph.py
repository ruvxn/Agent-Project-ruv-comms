import os
import sqlite3
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from backend.embedding.sql_setup import create_checkpoint_memory
from backend.model.states.graph_state.GraphState import GraphState
from backend.tools.tool_invoke_agent import tool_agent


def get_graph(state: GraphState) -> StateGraph:

    graph = StateGraph(GraphState)

    graph.add_node("tool_agent", tool_agent)

    graph.add_edge(START, "tool_agent")
    graph.add_edge("tool_agent", END)

    memory = create_checkpoint_memory()

    return graph.compile(checkpointer=memory)
