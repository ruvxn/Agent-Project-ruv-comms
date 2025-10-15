"""
criticality Classification Tool
classify customer reviews by detecting errors and assigning severity levels.
"""

import os
import json
from typing import Optional, List
from langchain_core.tools import tool

from src.config import OLLAMA_MODEL
from src.utils import RawReview, DetectedError
from src.nodes.detect_errors import detect_errors_with_ollama
from src.nodes.classify_criticality import classify_criticality
from src.database import load_unprocessed_reviews, get_connection


def load_reviews_by_ids(review_ids: List[str]) -> List[RawReview]:
    """
    Load specific reviews by their IDs from the database.
    """
    if not review_ids:
        return []

    conn = get_connection()
    cursor = conn.cursor()

    placeholders = ','.join(['%s'] * len(review_ids))
    query = f"""
        SELECT review_id, review, username, email, date, reviewer_name, rating
        FROM raw_reviews
        WHERE review_id IN ({placeholders})
        ORDER BY created_at DESC
    """

    cursor.execute(query, review_ids)
    rows = cursor.fetchall()

    reviews = []
    for row in rows:
        #convert datetime to string
        date_str = row[4]
        if hasattr(date_str, 'strftime'):
            date_str = date_str.strftime('%Y-%m-%d %H:%M:%S')

        reviews.append(RawReview(
            review_id=row[0],
            review=row[1],
            username=row[2],
            email=row[3],
            date=str(date_str),
            reviewer_name=row[5],
            rating=row[6]
        ))

    cursor.close()
    conn.close()

    return reviews


@tool
def classify_review_criticality(
    review_ids: Optional[List[str]] = None,
    limit: int = 10
) -> str:
    """Classify criticality of customer reviews and detect errors/issues using LLM analysis."""
    try:
        #cap limit for performance
        limit = min(limit, 50)

        #load reviews from db
        use_db = os.getenv("USE_DATABASE", "false").lower() == "true"

        if review_ids:
            if not use_db:
                return json.dumps({
                    "error": "Cannot load specific review IDs without database enabled (USE_DATABASE=true)",
                    "reviews": [],
                    "total_processed": 0
                })
            reviews = load_reviews_by_ids(review_ids)
        else:
            if use_db:
                reviews = load_unprocessed_reviews(batch_size=limit)
            else:
                #fallback to csv
                from src.nodes.load_reviews import load_reviews
                from src.config import DATA_PATH
                all_reviews = load_reviews(DATA_PATH)
                reviews = all_reviews[:limit]

        if not reviews:
            return json.dumps({
                "message": "No reviews found to process",
                "reviews": [],
                "total_processed": 0
            })

        results = []
        for review in reviews:
            #dtect errrs using the llm
            detected_errors = detect_errors_with_ollama(review, OLLAMA_MODEL)

        
            classified_errors = []
            for error in detected_errors:
                criticality = classify_criticality(error)
                classified_errors.append({
                    "error_summary": error.error_summary,
                    "error_type": error.error_type,
                    "criticality": criticality,
                    "rationale": error.rationale
                })

            results.append({
                "review_id": review.review_id,
                "review_text": review.review[:200] + "..." if len(review.review) > 200 else review.review,
                "rating": review.rating,
                "reviewer_name": review.reviewer_name,
                "errors": classified_errors,
                "error_count": len(classified_errors)
            })

        return json.dumps({
            "reviews": results,
            "total_processed": len(results),
            "review_ids": [r.review_id for r in reviews]
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Failed to classify reviews: {str(e)}",
            "reviews": [],
            "total_processed": 0
        })
