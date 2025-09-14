import datetime
import os
import chromadb
from dotenv import load_dotenv
from chromadb import Collection, PersistentClient

from backend.model.dto.PipelineState import PipelineState

load_dotenv()


def set_up_chroma_client():

    CHROMA_TABLE = os.getenv("CHROMA_TABLE")
    CHROMA_PATH = os.getenv("CHROMA_PATH")

    chroma_client = PersistentClient(path=CHROMA_PATH)

    collection = chroma_client.get_or_create_collection(
        name=CHROMA_TABLE,
        metadata={
            "description": "pdf chunks and summary",
            "created": str(datetime.now())
        })

    return collection


def insert_into_chroma(state: PipelineState):

    return
