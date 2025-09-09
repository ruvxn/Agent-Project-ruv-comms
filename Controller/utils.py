import json
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter

from Controller.db_setup.mysql_setup import *

load_dotenv()

CHUNK_SIZE = os.getenv("CHUNK_SIZE")
CHUNK_OVERLAP = os.getenv("CHUNK_OVERLAP")


def chunking(data: str) -> list[str]:
    """Data chuncking"""
    splitter = RecursiveCharacterTextSplitter(
        CHUNK_SIZE=CHUNK_SIZE,
        CHUNK_OVERLAP=CHUNK_OVERLAP
    )
    chunks = splitter.split_text(data)
    return chunks


def extract_first_json(text: str) -> dict:
    matches = re.findall(r"\{.*?\}", text, re.DOTALL)

    if not matches:
        raise ValueError("No JSON object found in LLM output")

    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse JSON from LLM output")

    raise ValueError("Failed to parse JSON from LLM output")
