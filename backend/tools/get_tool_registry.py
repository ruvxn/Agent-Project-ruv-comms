from backend.tools.chat_tool import chat_tool
from backend.tools.pdf_qa_tool import pdf_qa_tool


def get_tool_registry():
    return {
        "pdf_qa_tool": pdf_qa_tool(),
        "chat_tool": chat_tool(),
    }
