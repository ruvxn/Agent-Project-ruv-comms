from dataclasses import dataclass


@dataclass
class ReviewSummaryDTO:
    review: str
    review_id: str
