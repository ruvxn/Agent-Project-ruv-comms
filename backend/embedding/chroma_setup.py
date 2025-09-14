import datetime
import os
import chromadb
from dotenv import load_dotenv
from chromadb import Collection, PersistentClient

load_dotenv()


def set_up_chroma_client():

    CHROMA_REVIEW_TABLE = os.getenv("CHROMA_REVIEW_TABLE")
    CHROMA_PATH = os.getenv("CHROMA_PATH")

    chroma_client = PersistentClient(path=CHROMA_PATH)

    collection = chroma_client.get_or_create_collection(
        name=CHROMA_REVIEW_TABLE,
        metadata={
            "description": "review summary and tags",
            "created": str(datetime.now())
        })

    return collection


def insert_into_chroma(summarize_reviews: list):
    return
