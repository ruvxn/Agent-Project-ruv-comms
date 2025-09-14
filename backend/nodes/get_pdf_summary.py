import os
import dotenv
from backend.Model.DTO.PipelineState import PipelineState
from backend.utils.wrapper import node_log
from transformers import pipeline
from utils import chunking
import fitz

dotenv.load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
SUMMARIZER_MODEL = os.getenv("SUMMARIZER_MODEL")
SUMMARY_MAX_LENGTH = os.getenv("SUMMARY_MAX_LENGTH")

summary_pipeline = pipeline("summarization", model=SUMMARIZER_MODEL)


def chunked_summary_pdf(single_chunk: str) -> str:
    summary = summary_pipeline(
        single_chunk, max_length=SUMMARY_MAX_LENGTH,
        min_length=50, do_sample=False)
    return summary[0]["summary_text"].replace("\xa0", " ")


@node_log
def get_pdf_summary(state: PipelineState) -> str:
    summaries = []
    for single_page_pdf_text in state.chunked_pdf_text:
        for single_chunk in single_page_pdf_text.chunk:
            summaries.append(chunked_summary_pdf(single_chunk))

    summaries_string = " ".join(summaries)
    state.final_summary = chunked_summary_pdf(summaries_string)
    return state
