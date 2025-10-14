from typing import Annotated
from pydantic import BaseModel, Field, root_validator
from backend.model.states.graph_state.ConfigState import ConfigState
from backend.model.states.graph_state.SummaryState import SummaryState
from backend.model.states.qa_state.PdfState import PdfState
from backend.model.stores.LogStore import LogStore
from backend.model.stores.MessageStore import MessageStore
from frontend.utils import render_log, render_message


def merge_messages(current: MessageStore, new: MessageStore) -> MessageStore:
    if current is None:
        return new
    if new is None:
        return current

    for msg in new:
        if not current._message_exists(msg):
            current.append(msg)
            render_message(msg, current.message_placeholder)
    return current


def merge_logs(current: LogStore, new: LogStore) -> LogStore:
    if current is None:
        return new
    if new is None:
        return current

    for log in new:
        if log not in current:
            current.append(log)
            render_log(log, current.log_placeholder)
    return current


class GraphState(BaseModel):
    qa_state: PdfState = Field(
        default_factory=PdfState)
    summary_state: SummaryState = Field(default_factory=SummaryState)
    messages: Annotated[MessageStore, merge_messages] = Field(
        default_factory=MessageStore)
    logs: Annotated[LogStore, merge_logs] = Field(default_factory=LogStore)
    graph_config: ConfigState = Field(default_factory=ConfigState)
    collection_names_list: list[str] = Field(default_factory=list)

    model_config = {
        "arbitrary_types_allowed": True,
        "validate_default": False,
    }

    @root_validator(pre=True)
    def ensure_stores(cls, values):
        if values.get("messages") is None:
            values["messages"] = MessageStore()
        if values.get("logs") is None:
            values["logs"] = LogStore()
        return values
