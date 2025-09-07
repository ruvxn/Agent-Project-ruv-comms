from dataclasses import dataclass
from typing import Any


@dataclass
class JSONResponseDTO:
    success: bool
    message: str | None = None
    data: Any | None = None
    error: str | None = None
