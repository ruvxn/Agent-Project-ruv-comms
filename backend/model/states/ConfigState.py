from pydantic import BaseModel


class ConfigState(BaseModel):
    CHUNK_SIZE: int = 200
    CHUNK_OVERLAP: int = 100
    RAG_THRESHOLD: float = 0.15
    TOP_K: int = 10
    SUMMARY_MAX_LENGTH: int = 1000
    SUMMARY_MIN_LENGTH: int = 500
    SUMMARY_CHUNK_SIZE: int = 3000
    SUMMARY_CHUNK_OVERLAP: int = 3000
    SHOW_LOG: bool = True
