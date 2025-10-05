from typing import Optional
from pydantic import BaseModel, Field


class Meta(BaseModel):
    pdf_name: str = ""
    page_number: int = 0
    chunk_summary: str = ""


class PdfTextClass(BaseModel):
    meta: Meta = Meta()
    chunk: str = ""
    embedding: Optional[list[float]] = None
