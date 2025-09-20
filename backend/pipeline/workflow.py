from langgraph.graph import StateGraph, START
from backend.model.states.GraphState import GraphState
from backend.nodes.chat_agent import chat_agent
from backend.nodes.rag_agent import rag_agent
from backend.pipeline.get_pdf_ready_pipeline import get_pdf_ready_pipeline
from backend.pipeline.rag_router import rag_router


def get_graph(state: GraphState) -> StateGraph:

    graph = StateGraph(GraphState)

    graph.add_node("get_pdf_ready_pipeline", get_pdf_ready_pipeline)
    graph.add_node("router", lambda state: state)
    graph.add_node("rag_agent", rag_agent)
    graph.add_node("chat_agent", chat_agent)

    graph.add_edge(START, "chat_agent")
    graph.add_edge("chat_agent", "router")
    graph.add_edge("get_pdf_ready_pipeline", "rag_agent")
    graph.add_conditional_edges(
        "router",
        rag_router,
        {
            "TRUE": "get_pdf_ready_pipeline",
            "FALSE": "chat_agent",
        },
    )

    graph.set_entry_point("chat_agent")

    return graph.compile()
