from langgraph.graph import StateGraph, START, END
from backend.model.states.GraphState import GraphState
from backend.nodes.chat_agent import chat_agent
from backend.nodes.no_kb_agent import no_kb_agent
from backend.nodes.rag_agent import rag_agent
from backend.nodes.tool_agent import tool_agent
from backend.pipeline.get_pdf_ready_pipeline import get_pdf_ready_pipeline
from backend.pipeline.upload_check_router import upload_check_router
from backend.pipeline.rag_router import rag_router
from langgraph.checkpoint.memory import MemorySaver


def get_graph2(state: GraphState) -> StateGraph:

    graph = StateGraph(GraphState)

    graph.add_node("tool_agent", tool_agent)

    graph.add_edge(START, "tool_agent")
    graph.add_edge("tool_agent", END)

    return graph.compile()
