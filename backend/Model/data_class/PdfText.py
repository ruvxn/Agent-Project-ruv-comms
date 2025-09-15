from pydantic import BaseModel


class Meta(BaseModel):
    pdf_name: str
    page_number: int
    chunk_summary: str


class PdfText(BaseModel):
    chunk: str
    meta: Meta
