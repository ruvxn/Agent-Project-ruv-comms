from attr import asdict
from backend.utils.utils import chunking
from backend.utils.wrapper import node_log
import fitz
import os
import dotenv

from Model.DTO.PdfText import Meta, PdfText

dotenv.load_dotenv()

PDF_NAME = os.getenv("PDF_NAME")


@node_log
def node_extract_pdf_to_chunk(state: dict) -> dict:
    pdf = fitz.open(state["pdf_path"])
    pdf_text_list: list[PdfText] = []
    for page_num, page in enumerate(pdf, start=1):
        page_text = page.get_text().strip()
        if not page_text:
            continue
        chunk_page_text = chunking(page_text)
        meta = Meta(
            pdf_title=PDF_NAME,
            page_number=page_num,
            chunk_count=len(chunk_page_text)
        )
        pdf_text_list.append(PdfText(chunk=chunk_page_text, meta=meta))

    state["chunked_pdf_text"] = pdf_text_list

    return state
