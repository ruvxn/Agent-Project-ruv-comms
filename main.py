from backend.model.states.StateManager import StateManager
from frontend.home_ui import render_chat_section, render_file_uploader, render_sidebar
from typing import Any
from nicegui import ui
from langgraph.checkpoint.serde import jsonplus
from langgraph.checkpoint.serde.jsonplus import _msgpack_default
from langgraph.checkpoint.serde.jsonplus import _option
from langgraph.checkpoint.serde.jsonplus import ormsgpack

# Reference from: https://github.com/langchain-ai/langgraph/issues/4956#issuecomment-3135374853


def message_to_dict(msg):
    """
    Recursively convert a message or object into a dict/str (safe for serialization).
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


def start():
    monkey_patch()
    state = StateManager.get_state()

    with ui.row().classes('w-full flex h-screen p-6 gap-6'):

        with ui.column().classes(' flex-3 w-1/4 h-full overflow-y-auto border rounded-lg p-4 bg-gray-50 shadow-sm'):
            render_sidebar()

        with ui.column().classes('flex-9  w-3/4 h-full overflow-y-auto border rounded-lg p-4 bg-gray-50 shadow-sm'):
            render_chat_section()


start()
ui.run(title='Graph AI Chat', reload=True, port=8080)
