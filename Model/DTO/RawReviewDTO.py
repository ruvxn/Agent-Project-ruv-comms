from dataclasses import dataclass
from datetime import datetime


@dataclass
class RawReviewDTO:
    id: str
    user_id: str | None
    purchase_id: str | None
    review_title: str
    review_body: str
    create_time_stamp: datetime
    insert_time_stamp: datetime
