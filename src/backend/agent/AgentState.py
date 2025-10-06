from typing import Annotated
from typing_extensions import TypedDict, List, Any
from langgraph.graph.message import add_messages


class State(TypedDict):
    """An agent state"""
    messages: Annotated[list, add_messages]
    tools: List[Any]
    plan: str
    critique: str
