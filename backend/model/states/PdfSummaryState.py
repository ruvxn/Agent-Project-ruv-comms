from pydantic import BaseModel


class PdfSummaryClass(BaseModel):
    pdf_name: str = ""
    final_summary: str = ""


class PdfSummaryState(BaseModel):
    PdfSummary: list[PdfSummaryClass] = []
