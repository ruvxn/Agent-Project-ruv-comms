from dotenv import load_dotenv
import os
from backend.model.dto.PipelineState import PipelineState

from backend.nodes.extract_pdf_to_chunk import extract_pdf_to_chunk
from backend.nodes.get_pdf_summary import get_pdf_summary


load_dotenv()
PDF_PATH = os.getenv("PDF_PATH")

state = PipelineState()
state.pdf_path = PDF_PATH

state = extract_pdf_to_chunk(state)
state = get_pdf_summary(state)

print("final_summary: ", state.final_summary)
print("state message: ", state.message)
