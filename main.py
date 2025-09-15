# from dotenv import load_dotenv
# import os
from backend.model.data_class.PipelineState import PipelineState
from frontend.home_ui import render_main_section, render_side_bar

# load_dotenv()
# PDF_PATH = os.getenv("PDF_PATH")


state = PipelineState()
# state.pdf_path = PDF_PATH


state = PipelineState()

state = render_side_bar(state)
render_main_section(state)
