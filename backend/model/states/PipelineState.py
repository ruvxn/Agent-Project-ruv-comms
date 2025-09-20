from pydantic import BaseModel
from typing import List
from backend.model.dto.PdfText import PdfText


class PipelineState(BaseModel):
    pdf_path: str = ""
    pdf_name: str = ""
    chunked_pdf_text: List[PdfText] = []
    logs: list[str] = []
    final_summary: str = ""
