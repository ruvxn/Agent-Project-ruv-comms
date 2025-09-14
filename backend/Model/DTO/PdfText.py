from dataclasses import dataclass


@dataclass
class Meta:
    pdf_title: str
    page_number: int
    chunk_count: int


@dataclass
class PdfText:
    chunk: list[str]
    meta: Meta
