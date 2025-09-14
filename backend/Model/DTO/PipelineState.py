from pydantic import BaseModel
from typing import List
from backend.Model.DTO.PdfText import PdfText


class PipelineState(BaseModel):
    pdf_path: str = ""
    chunked_pdf_text: List[PdfText] = []
    final_summary: str = ""
    message: List[str] = []
