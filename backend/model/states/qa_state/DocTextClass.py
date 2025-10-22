from typing import Optional
from pydantic import BaseModel, Field


class Meta(BaseModel):
    doc_name: str = ""
    page_number: int = 0


class DocTextClass(BaseModel):
    meta: Meta = Meta()
    chunk: str = ""
    embedding: Optional[list[float]] = None
