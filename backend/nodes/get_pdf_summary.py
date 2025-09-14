import os
import dotenv
from backend.model.dto.PipelineState import PipelineState
from backend.utils.utils import chunked_summary_pdf, clean_text

from backend.utils.wrapper import node_log

dotenv.load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")


@node_log
def get_pdf_summary(state: PipelineState) -> PipelineState:
    summaries = []
    for single_page_pdf_text in state.chunked_pdf_text:
        summaries.append(chunked_summary_pdf(
            clean_text(single_page_pdf_text.chunk)))

    if summaries:
        summaries_string = " ".join(summaries)
        state.final_summary = chunked_summary_pdf(summaries_string)
    else:
        state.final_summary = "No content to summarize."

    return state
