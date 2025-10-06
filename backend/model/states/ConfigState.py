from pydantic import BaseModel


class ConfigState(BaseModel):
    CHUNK_SIZE: int = 200
    CHUNK_OVERLAP: int = 100
    RAG_THRESHOLD: float = 0.46
    TOP_K: int = 3
    SUMMARY_MAX_LENGTH: int = 100
    SUMMARY_CHUNK_SIZE: int = 3000
    SUMMARY_CHUNK_OVERLAP: int = 3000
    SHOW_LOG: bool = True
