from backend.embedding.chroma_setup import get_all_collection_name, get_collection
from backend.model.states.GraphState import GraphState
from backend.model.states.ToolReturnClass import ToolReturnClass
from backend.nodes.rag_agent import rag_agent
from backend.nodes.rag_retrieval_node import rag_retrieval_node
from backend.pipeline.build_qa_graph import build_qa_graph
from backend.pipeline.get_pdf_ready_pipeline import get_pdf_ready_pipeline
from backend.pipeline.rag_router import rag_router
from backend.pipeline.workflow import get_graph
from backend.tools.base_tool import BaseTool
from backend.utils import get_embedding, get_user_input, log_decorator
from langchain_core.tools import tool
import streamlit as st


class pdf_qa_tool(BaseTool):
    """Return answers based on top-k knowledge base chunks"""

    def __init__(self) -> None:
        super().__init__()
        self.subgraph = build_qa_graph()

    def invoke(self, arg: dict) -> ToolReturnClass:
        state: GraphState = arg["state"]
        qa_state: GraphState = self.subgraph.invoke(state)
        if isinstance(qa_state, dict):
            qa_state = GraphState(**qa_state)
        return ToolReturnClass(
            state=qa_state,
            agent_response=qa_state.messages.ai_response_list[-1] if qa_state.messages.ai_response_list else "No response",
            meta={"tool_name": "pdf_qa_tool"}
        )
