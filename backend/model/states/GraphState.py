from typing import Annotated, List
from pydantic import BaseModel, Field, root_validator
from backend.model.states.ConfigState import ConfigState
from backend.model.states.qa_state.PdfState import PdfState
from backend.model.stores.LogStore import LogStore
from backend.model.stores.MessageStore import MessageStore
from frontend.utils import render_log, render_message


class GraphState(BaseModel):
    qa_state: PdfState = Field(default_factory=PdfState)
    messages: Annotated[MessageStore, render_message] = Field(
        default_factory=MessageStore)
    logs: Annotated[LogStore, render_log] = Field(default_factory=LogStore)
    graph_config: ConfigState = Field(default_factory=ConfigState)
    collection_names_list: list[str] = Field(default_factory=list)

    model_config = {
        "arbitrary_types_allowed": True,
        "validate_default": False
    }

    @root_validator(pre=True)
    def ensure_stores(cls, values):
        if values.get("messages") is None:
            values["messages"] = MessageStore()
        if values.get("logs") is None:
            values["logs"] = LogStore()
        return values
