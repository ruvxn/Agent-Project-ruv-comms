from functools import wraps
from copy import deepcopy
import json
import re
import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from functools import wraps
import streamlit as st

load_dotenv()

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 20))
SUMMARIZER_MODEL = os.getenv("SUMMARIZER_MODEL")
SUMMARY_MAX_LENGTH = int(os.getenv("SUMMARY_MAX_LENGTH", 100))
EMBED_MODEL = os.getenv("EMBED_MODEL")

summary_pipeline = pipeline("summarization", model=SUMMARIZER_MODEL)


def log_decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            state = st.session_state.state
            if hasattr(state, "logs") and state.logs is not None:
                state.logs.append(f"[{function.__name__}] called")
            return function(*args, **kwargs)
        except Exception as e:
            state.logs.append(f"[{function.__name__}] ERROR. {e}")
            raise
    return wrapper


@log_decorator
def get_chunk(data: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_text(data)
    return chunks


@log_decorator
def get_embedding(chunk: str):
    embed_model = SentenceTransformer(model_name_or_path=EMBED_MODEL)
    embed_result = embed_model.encode(
        chunk, show_progress_bar=True)
    return embed_result


@log_decorator
def single_chunk_summary(single_chunk: str) -> str:
    single_chunk_len = len(single_chunk.split())
    max_new = max(1, single_chunk_len // 2)
    min_len = min(50, single_chunk_len)
    summary = summary_pipeline(
        single_chunk,
        max_new_tokens=max_new,
        min_length=min_len,
        do_sample=False
    )
    return summary[0]["summary_text"].replace("\xa0", " ")


@log_decorator
def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\xa0", " ").replace("\u200b", "")
    text = text.replace("\n", " ").replace("\t", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"•+", "-", text)
    text = text.strip()
    return text
