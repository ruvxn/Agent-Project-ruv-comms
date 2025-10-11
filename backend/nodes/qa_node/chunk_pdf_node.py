from attr import asdict
import streamlit
from backend.model.states.GraphState import GraphState
import fitz
import os
from dotenv import load_dotenv
from backend.model.states.qa_state.PdfTextClass import Meta, PdfTextClass
from backend.utils import single_chunk_summary, get_chunk, clean_text, log_decorator

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")
PDF_NAME = os.path.splitext(os.path.basename(PDF_PATH))[0]


@log_decorator
def chunk_pdf_node(state: GraphState) -> dict:
    state = streamlit.session_state.state
    pdf = fitz.open(state.qa_state.pdf_path)
    pdf_text_list: list[PdfTextClass] = []
    for page_num, page in enumerate(pdf, start=1):
        page_text = page.get_text().strip()
        if not page_text:
            continue
        chunk_page_text = get_chunk(clean_text(page_text), state)
        for single_chunk in chunk_page_text:
            # chunk_summary = single_chunk_summary(single_chunk)
            meta = Meta(
                pdf_name=PDF_NAME,
                page_number=page_num,
                # chunk_summary=chunk_summary
            )
            pdf_text_list.append(
                PdfTextClass(chunk=single_chunk, meta=meta, embedding=[]))

    state.qa_state.chunked_pdf_text = pdf_text_list
    state.qa_state.pdf_name = PDF_NAME
    return state
