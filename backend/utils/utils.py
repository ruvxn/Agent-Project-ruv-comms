from functools import wraps
from copy import deepcopy
import json
import re
import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import pipeline

load_dotenv()

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 20))
SUMMARIZER_MODEL = os.getenv("SUMMARIZER_MODEL")
SUMMARY_MAX_LENGTH = int(os.getenv("SUMMARY_MAX_LENGTH", 100))

summary_pipeline = pipeline("summarization", model=SUMMARIZER_MODEL)


def chunking(data: str) -> list[str]:
    """Data chuncking"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_text(data)
    return chunks


def chunked_summary_pdf(single_chunk: str) -> str:
    summary = summary_pipeline(
        single_chunk, max_length=SUMMARY_MAX_LENGTH,
        min_length=50, do_sample=False)
    return summary[0]["summary_text"].replace("\xa0", " ")


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\xa0", " ").replace("\u200b", "")
    text = text.replace("\n", " ").replace("\t", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"•+", "-", text)
    text = text.strip()
    return text
