from pydantic import BaseModel, Field
from typing import List, Literal, Optional
import hashlib

Criticality = Literal["Critical", "Major", "Minor", "Suggestion", "None"]

#columns expteceted from the datasset as inputs
class RawReview(BaseModel):
    review_id: str
    review: str
    username: str
    email: str
    date: str
    reviewer_name: str
    rating: int

#detetcted error LLM output before it is normalised
class DetectedError(BaseModel):
    error_summary: str
    error_type: List[str] = Field(default_factory=list)
    rationale: str

# Sentiment analysis data
class SentimentData(BaseModel):
    """Complete sentiment analysis for a review"""
    review_id: str
    overall_sentiment: str  # positive, negative or neutral
    overall_confidence: float  # 0.0-1.0
    sentiment_polarity: float  # -1.0 to +1.0

# normalised error - ready to log
class EnrichedError(BaseModel):
    review: RawReview
    error: DetectedError
    criticality: Criticality
    error_hash: str

    #Sentiment enrichment
    sentiment_data: Optional[SentimentData] = None
    sentiment_influenced_criticality: bool = False

#deduplication
def hash_error(review_id: str, summary: str) -> str:
    key = f"{review_id}|{summary}".encode("utf-8")
    return hashlib.sha256(key).hexdigest()[:16]
