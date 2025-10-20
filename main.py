
from backend.model.states.StateManager import StateManager
from frontend import home_ui
from typing import Any
import tempfile
from langgraph.checkpoint.serde import jsonplus
from langgraph.checkpoint.serde.jsonplus import _msgpack_default
from langgraph.checkpoint.serde.jsonplus import _option
from langgraph.checkpoint.serde.jsonplus import ormsgpack
from nicegui import ui, app, events
from backend.model.states.graph_state.GraphState import GraphState

def message_to_dict(msg):
    """
    Recursively convert a message or object into a dict/str (safe for serialization).
    Reference from: https://github.com/langchain-ai/langgraph/issues/4956#issuecomment-3135374853
    """
    if hasattr(msg, "to_dict"):
        return msg.to_dict()
    elif isinstance(msg, dict):
        return {k: message_to_dict(v) for k, v in msg.items()}
    elif isinstance(msg, (list, tuple)):
        return [message_to_dict(x) for x in msg]
    elif isinstance(msg, (str, int, float, bool, type(None))):
        return msg
    else:
        print("Serialization Fallback, type:", type(msg))
        print(msg)
        return {"role": getattr(msg, "role", "user"), "content": str(getattr(msg, "content", msg))}


def _msgpack_enc(data: Any) -> bytes:
    return ormsgpack.packb(message_to_dict(data), default=_msgpack_default, option=_option)


def monkey_patch():
    setattr(jsonplus, "_msgpack_enc", _msgpack_enc)







state = StateManager.get_state()
@ui.page("/")
def start():
    monkey_patch()
    #home_ui.render_sidebar(state)
    new_state = home_ui.render_main_section(state)



ui.run()
