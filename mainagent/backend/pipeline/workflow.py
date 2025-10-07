from langgraph.graph import StateGraph, START, END
from mainagent.backend.model.states.GraphState import GraphState
from mainagent.backend.tools.tool_agent import tool_agent


def get_graph(state: GraphState) -> StateGraph:

    graph = StateGraph(GraphState)

    graph.add_node("tool_agent", tool_agent)

    graph.add_edge(START, "tool_agent")
    graph.add_edge("tool_agent", END)

    return graph.compile()
