from typing import Annotated, List
from pydantic import BaseModel, Field, root_validator
from backend.model.states.PdfState import PdfState
from backend.model.stores.LogStore import LogStore
from backend.model.stores.MessageStore import MessageStore
from frontend.utils import render_log, render_message


class GraphState(BaseModel):
    pdf: PdfState = Field(default_factory=PdfState)
    messages: Annotated[MessageStore, render_message] = Field(
        default_factory=MessageStore)
    logs: Annotated[LogStore, render_log] = Field(default_factory=LogStore)
    collection_names_list: list[str] = []

    model_config = {
        "arbitrary_types_allowed": True
    }

    @root_validator(pre=True)
    def ensure_stores(cls, values):
        if values.get("messages") is None:
            values["messages"] = MessageStore()
        if values.get("logs") is None:
            values["logs"] = LogStore()
        return values
