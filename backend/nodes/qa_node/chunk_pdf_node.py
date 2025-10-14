from attr import asdict
import streamlit
from backend.model.states.StateManager import StateManager
from backend.model.states.graph_state.GraphState import GraphState
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
    pdf = fitz.open(state.qa_state.pdf_path)
    pdf_text_list: list[PdfTextClass] = []
    for page_num, page in enumerate(pdf, start=1):
        page_text = page.get_text().strip()
        if not page_text:
            continue
        chunk_page_text = get_chunk(
            clean_text(page_text),
            state.graph_config.CHUNK_SIZE,
            state.graph_config.CHUNK_OVERLAP
        )
        for single_chunk in chunk_page_text:
            meta = Meta(
                pdf_name=PDF_NAME,
                page_number=page_num,
            )
            pdf_text_list.append(
                PdfTextClass(chunk=single_chunk, meta=meta, embedding=[]))

    state.qa_state.chunked_pdf_text = pdf_text_list
    state.qa_state.pdf_name = PDF_NAME
    return state
