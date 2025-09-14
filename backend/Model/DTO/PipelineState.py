from pydantic import BaseModel
from typing import List
from backend.model.dto.PdfText import PdfText


class PipelineState(BaseModel):
    pdf_path: str = ""
    chunked_pdf_text: List[PdfText] = []
    message: List[str] = []
    final_summary: str = ""
