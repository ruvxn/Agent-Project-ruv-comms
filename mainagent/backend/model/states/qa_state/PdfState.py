from pydantic import BaseModel

from mainagent.backend.model.states.qa_state.PdfTextClass import PdfTextClass


class PdfState(BaseModel):
    pdf_path: str = ""
    pdf_name: str = ""
    chunked_pdf_text: list[PdfTextClass] = []
    final_summary: str = ""
    top_k_kb: str = ""
    is_upload: bool = False
    is_processed: bool = False
