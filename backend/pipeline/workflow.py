from langgraph.graph import StateGraph, START, END
from backend.model.states.GraphState import GraphState
from backend.nodes.chat_agent import chat_agent
from backend.nodes.no_kb_agent import no_kb_agent
from backend.nodes.rag_agent import rag_agent
from backend.pipeline.get_pdf_ready_pipeline import get_pdf_ready_pipeline
from backend.pipeline.upload_check_router import upload_check_router
from backend.pipeline.rag_router import rag_router
from langgraph.checkpoint.memory import MemorySaver


def get_graph(state: GraphState) -> StateGraph:

    graph = StateGraph(GraphState)

    graph.add_node("upload_check_router", lambda state: state)
    graph.add_node("get_pdf_ready_pipeline", get_pdf_ready_pipeline)
    graph.add_node("router", lambda state: state)
    graph.add_node("rag_agent", rag_agent)
    graph.add_node("chat_agent", chat_agent)
    graph.add_node("no_kb_agent", no_kb_agent)

    graph.add_edge(START, "upload_check_router")
    graph.add_edge("get_pdf_ready_pipeline", "router")

    graph.add_conditional_edges(
        "router",
        rag_router,
        {
            "TRUE": "rag_agent",
            "FALSE": END,
            "NO_KB": "no_kb_agent",
        },
    )
    graph.add_conditional_edges(
        "upload_check_router",
        upload_check_router,
        {
            "TRUE": "get_pdf_ready_pipeline",
            "FALSE": "chat_agent",
        },
    )

    graph.set_entry_point("upload_check_router")
    graph.set_finish_point("no_kb_agent")
    graph.set_finish_point("rag_agent")

    short_term_memory = MemorySaver()

    return graph.compile(checkpointer=short_term_memory)
