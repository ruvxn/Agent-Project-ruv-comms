
from backend.model.states.GraphState import GraphState
from backend.model.states.tool_state.ToolReturnClass import ToolReturnClass
from backend.pipeline.qa_tool.build_qa_graph import build_qa_graph
from backend.pipeline.qa_tool.get_pdf_ready_pipeline import get_pdf_ready_pipeline
from backend.pipeline.summary_tool.build_summary_graph import build_summary_graph
from backend.tools.base_tool import BaseTool
import streamlit as st


class summary_tool(BaseTool):
    """Return Final Summary"""

    def __init__(self) -> None:
        super().__init__()
        self.subgraph = build_summary_graph()

    def invoke(self, arg: dict) -> ToolReturnClass:
        state: GraphState = arg["state"]

        if not st.session_state.state.qa_state.is_processed:
            get_pdf_ready_pipeline(state)

        summary_state: GraphState = self.subgraph.invoke(state)
        if isinstance(summary_state, dict):
            summary_state = GraphState(**summary_state)
        return ToolReturnClass(
            state=summary_state,
            agent_response=state.summary_state.final_summary,
            meta={"tool_name": "summary_tool"}
        )
