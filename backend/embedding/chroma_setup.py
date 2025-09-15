from datetime import datetime
import os
import chromadb
import uuid
from dotenv import load_dotenv
from chromadb import Collection, PersistentClient
from sentence_transformers import SentenceTransformer
from backend.model.data_class.PipelineState import PipelineState

load_dotenv()
EMBED_MODEL = os.getenv("EMBED_MODEL")


def set_up_chroma_client(state: PipelineState):
    CHROMA_PATH = os.getenv("CHROMA_PATH")

    chroma_client = PersistentClient(path=CHROMA_PATH)

    collection = chroma_client.get_or_create_collection(
        name=state.pdf_name,
        metadata={
            "description": f"pdf {state.pdf_name} chunks and summary",
            "created": str(datetime.now())
        })
    state.logs.append(f"collection {state.pdf_name} created or found")
    return collection


def insert_into_chroma(state: PipelineState) -> PipelineState:
    collection = set_up_chroma_client(state)

    exist_embeding = collection.get(
        where={"pdf_name": state.pdf_name},
        limit=1
    )

    if exist_embeding["documents"] and exist_embeding["documents"][0]:
        state.logs.append("PDF chunk already embedded, skipping.")
        return state

    chunked_pdf_text = state.chunked_pdf_text
    texts = [pdf_text.chunk for pdf_text in chunked_pdf_text]

    embed_model = SentenceTransformer(EMBED_MODEL)
    embedding = embed_model.encode(texts, show_progress_bar=True)
    total_chunk = len(state.chunked_pdf_text)

    for i, pdf_text in enumerate(chunked_pdf_text, start=0):
        collection.add(
            ids=[str(uuid.uuid4())],
            embeddings=[embedding[i]],
            documents=[pdf_text.chunk],
            metadatas=[pdf_text.meta.__dict__]
        )
        state.logs.append(
            f"Inserted {i+1}/{total_chunk} chunk into Chroma.")
    summary_embedding = embed_model.encode(
        [state.final_summary], show_progress_bar=True)
    collection.add(
        ids=[str(uuid.uuid4())],
        embeddings=summary_embedding.tolist(),
        documents=[state.final_summary],
        metadatas=[{"pdf_name": state.pdf_name}]
    )
    state.logs.append(
        f"Inserted final_summary: {state.final_summary}.")
    return state
