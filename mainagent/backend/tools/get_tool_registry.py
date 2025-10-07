from mainagent.backend.tools.chat_tool import chat_tool
from mainagent.backend.tools.qa_tool import qa_tool
from mainagent.backend.tools.summary_tool import summary_tool


def get_tool_registry():
    return {
        "qa_tool": qa_tool(),
        "chat_tool": chat_tool(),
        "summary_tool": summary_tool(),
    }
