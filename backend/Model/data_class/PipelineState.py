from pydantic import BaseModel
from typing import List, Union
from backend.model.data_class.PdfText import PdfText
from langchain_core.messages import HumanMessage, AIMessage


class PipelineState(BaseModel):
    # pdf
    pdf_path: str = ""
    pdf_name: str = ""
    chunked_pdf_text: list[PdfText] = []
    logs: list[str] = []
    final_summary: str = ""

    # UI controller
    use_rag: bool = False

    # agent
    messages: list[Union[HumanMessage, AIMessage]] = []
