from attr import asdict
from backend.model.data_class.PdfText import Meta, PdfText
from backend.model.data_class.PipelineState import PipelineState
from backend.utils.utils import chunked_summary_pdf, chunking, clean_text
import fitz
import os
import dotenv

dotenv.load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")
PDF_NAME = os.path.splitext(os.path.basename(PDF_PATH))[0]


def extract_pdf_to_chunk(state: PipelineState) -> dict:
    pdf = fitz.open(state.pdf_path)
    pdf_text_list: list[PdfText] = []
    for page_num, page in enumerate(pdf, start=1):
        page_text = page.get_text().strip()
        if not page_text:
            continue
        chunk_page_text = chunking(clean_text(page_text))
        for single_chunk in chunk_page_text:
            chunk_summary = chunked_summary_pdf(single_chunk)
            meta = Meta(
                pdf_name=PDF_NAME,
                page_number=page_num,
                chunk_summary=chunk_summary
            )
            pdf_text_list.append(
                PdfText(chunk=single_chunk, meta=meta))

    state.chunked_pdf_text = pdf_text_list
    state.pdf_name = PDF_NAME
    print(f"state.chunked_pdf_text:{state.chunked_pdf_text}")

    return state
