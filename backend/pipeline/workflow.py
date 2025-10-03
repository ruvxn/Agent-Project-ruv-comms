from langgraph.graph import StateGraph, START, END
from backend.model.states.GraphState import GraphState
from backend.nodes.tool_agent import tool_agent


def get_graph(state: GraphState) -> StateGraph:

    graph = StateGraph(GraphState)

    graph.add_node("tool_agent", tool_agent)

    graph.add_edge(START, "tool_agent")
    graph.add_edge("tool_agent", END)

    return graph.compile()
