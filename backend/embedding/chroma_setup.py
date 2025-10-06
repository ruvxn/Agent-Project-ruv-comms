from datetime import datetime
import os
import hashlib
from dotenv import load_dotenv
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
import streamlit
from backend.model.states.GraphState import GraphState
from backend.utils import get_embedding, log_decorator

load_dotenv()

CHROMA_PATH = os.getenv("CHROMA_PATH")
PDF_SUMMARY_COLLECTION = os.getenv("PDF_SUMMARY_COLLECTION")


@log_decorator
def get_or_create_collection(state: GraphState):
    state = streamlit.session_state.state
    if not state.qa_state.pdf_name:
        state.qa_state.pdf_name = PDF_NAME = os.path.splitext(
            os.path.basename(state.qa_state.pdf_path))[0]

    chroma_client = PersistentClient(path=CHROMA_PATH)

    collection = chroma_client.get_or_create_collection(
        name=state.qa_state.pdf_name,
        metadata={
            "description": f"pdf {state.qa_state.pdf_name} chunks and chunk summary",
            "created": str(datetime.now())
        })
    state.logs.append(
        f"[collection] {state.qa_state.pdf_name} created or found")
    return collection


@log_decorator
def get_all_collection_name(state: GraphState):
    state = streamlit.session_state.state
    client = PersistentClient(path=CHROMA_PATH)
    collections = client.list_collections()
    collection_names_list = [c.name for c in collections]
    state.collection_names_list = collection_names_list


@log_decorator
def get_or_create_summary_collection():
    state = streamlit.session_state.state

    chroma_client = PersistentClient(path=CHROMA_PATH)

    collection = chroma_client.get_or_create_collection(
        name=PDF_SUMMARY_COLLECTION,
        metadata={
            "description": f"pdf {PDF_SUMMARY_COLLECTION} file summary",
            "created": str(datetime.now())
        })
    state.logs.append(
        f"[collection] {PDF_SUMMARY_COLLECTION} created or found")
    return collection


@log_decorator
def get_collection(collection_name: str):
    chroma_client = PersistentClient(CHROMA_PATH)
    try:
        collection = chroma_client.get_collection(name=collection_name)
        if collection and collection.count():
            return collection
        return None
    except Exception:
        return None


@log_decorator
def insert_chunks(state: GraphState) -> GraphState:
    state = streamlit.session_state.state
    collection = get_or_create_collection(state)

    chunked_pdf_text = state.qa_state.chunked_pdf_text
    total_chunk = len(state.qa_state.chunked_pdf_text)

    for i, pdf_text in enumerate(chunked_pdf_text, start=0):

        if pdf_text.embedding is None:
            state.logs.append(f"Skipping chunk {i}: no embedding found.")
            continue

        exist_chunk = collection.get(ids=[chunk_id(pdf_text.chunk)])
        if exist_chunk["documents"]:
            state.logs.append(f"Skipping chunk {i}: chunk already embedded.")
            continue

        collection.add(
            ids=[chunk_id(pdf_text.chunk)],
            embeddings=[pdf_text.embedding],
            documents=[pdf_text.chunk],
            metadatas=[pdf_text.meta.__dict__]
        )
        state.logs.append(
            f"Inserted {i+1}/{total_chunk} chunk into Chroma.")

    return state


@log_decorator
def insert_pdf_summary(state: GraphState) -> GraphState:
    state = streamlit.session_state.state

    if state.qa_state.final_summary:
        return

    chroma_client = PersistentClient(path=CHROMA_PATH)

    collection = chroma_client.get_or_create_collection(
        name=PDF_SUMMARY_COLLECTION,
        metadata={
            "description": "user upload pdf file summary",
            "created": str(datetime.now()),
            "pdf_name": state.qa_state.pdf_name
        })

    exist_chunk = collection.get(ids=[chunk_id(
        state.qa_state.final_summary)]) if state.qa_state.final_summary else None
    if exist_chunk and exist_chunk["documents"]:
        state.logs.append(
            f"Skipping final_summary: final_summary already embedded.")

    summary_embedding = get_embedding([state.qa_state.final_summary])

    collection.add(
        ids=[chunk_id(state.qa_state.final_summary)],
        embeddings=summary_embedding.tolist(),
        documents=[state.qa_state.final_summary],
        metadatas=[{"pdf_name": state.qa_state.pdf_name}]
    )
    state.logs.append(
        f"Inserted final_summary: {state.qa_state.final_summary}.")

    return state


def chunk_id(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()
