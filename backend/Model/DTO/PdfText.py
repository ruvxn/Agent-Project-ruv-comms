from dataclasses import dataclass


@dataclass
class Meta:
    pdf_name: str
    page_number: int
    chunk_summary: str


@dataclass
class PdfText:
    chunk: str
    meta: Meta
