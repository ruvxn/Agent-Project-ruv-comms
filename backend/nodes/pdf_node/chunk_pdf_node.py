from attr import asdict
import streamlit
from backend.embedding.chroma_setup import insert_data_row
from backend.model.states.StateManager import StateManager
from backend.model.states.graph_state.GraphState import GraphState
import fitz
import os
from dotenv import load_dotenv
from backend.model.states.qa_state.DocTextClass import Meta, DocTextClass
from backend.utils import get_embedding, single_chunk_summary, get_chunk, clean_text, log_decorator

load_dotenv()

doc_path = os.getenv("DOC_PATH")
doc_name = os.path.splitext(os.path.basename(doc_path))[0]


@log_decorator
def chunk_pdf_node(state: GraphState) -> dict:
    pdf = fitz.open(state.qa_state.doc_path)
    pdf_text_list: list[DocTextClass] = []
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
                doc_name=doc_name,
                referenece_number=page_num,
            )
            pdf_text_list.append(
                DocTextClass(chunk=single_chunk, meta=meta))

            embedding = get_embedding(single_chunk)

            insert_data_row(single_chunk, embedding, meta.__dict__)

    state.qa_state.chunked_doc_text = pdf_text_list
    return state
