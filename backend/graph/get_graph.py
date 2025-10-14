from langgraph.graph import StateGraph, START, END
from backend.model.states.graph_state.GraphState import GraphState
from backend.tools.tool_invoke_agent import tool_agent
from langgraph.checkpoint.memory import InMemorySaver


def get_graph(state: GraphState) -> StateGraph:

    graph = StateGraph(GraphState)

    graph.add_node("tool_agent", tool_agent)

    graph.add_edge(START, "tool_agent")
    graph.add_edge("tool_agent", END)

    checkpointer = InMemorySaver()

    return graph.compile()
