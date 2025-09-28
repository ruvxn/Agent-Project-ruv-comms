from pydantic import BaseModel
from typing import List
from backend.model.states.PdfTextClass import PdfTextClass


class PipelineState(BaseModel):
    pdf_path: str = ""
    pdf_name: str = ""
    chunked_pdf_text: List[PdfTextClass] = []
    logs: list[str] = []
    final_summary: str = ""
