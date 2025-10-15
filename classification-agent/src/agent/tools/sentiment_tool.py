"""
sentiment analysis tool
analyzes emotional tone and sentiment of customer reviews using DeBERTa transformer model.
"""

import os
import json
from typing import Optional, List
from langchain_core.tools import tool

from src.utils import RawReview
from src.nodes.sentiment_analysis import analyze_review_sentiment as analyze_sentiment_node
from src.database import load_unprocessed_reviews
from src.agent.tools.criticality_tool import load_reviews_by_ids


@tool
def analyze_review_sentiment(
    review_ids: Optional[List[str]] = None,
    limit: int = 10
) -> str:
    """Analyze sentiment and emotional tone of customer reviews using DeBERTa transformer model."""
    try:
        #check if sentiment is enabled
        if os.getenv("ENABLE_SENTIMENT", "true").lower() == "false":
            return json.dumps({
                "error": "Sentiment analysis is disabled (ENABLE_SENTIMENT=false in config)",
                "sentiments": [],
                "total_analyzed": 0
            })

  
        limit = min(limit, 50)

        #load reviews
        use_db = os.getenv("USE_DATABASE", "false").lower() == "true"

        if review_ids:
            if not use_db:
                return json.dumps({
                    "error": "Cannot load specific review IDs without database enabled (USE_DATABASE=true)",
                    "sentiments": [],
                    "total_analyzed": 0
                })
            reviews = load_reviews_by_ids(review_ids)
        else:
            if use_db:
                reviews = load_unprocessed_reviews(batch_size=limit)
            else:
                #csv fallback
                from src.nodes.load_reviews import load_reviews
                from src.config import DATA_PATH
                all_reviews = load_reviews(DATA_PATH)
                reviews = all_reviews[:limit]

        if not reviews:
            return json.dumps({
                "message": "No reviews found to analyze",
                "sentiments": [],
                "total_analyzed": 0
            })

        #snetiment analysis for each review
        results = []
        for idx, review in enumerate(reviews, 1):
            try:
                sentiment_data = analyze_sentiment_node(review)

                results.append({
                    "review_id": review.review_id,
                    "review_text": review.review[:200] + "..." if len(review.review) > 200 else review.review,
                    "rating": review.rating,
                    "reviewer_name": review.reviewer_name,
                    "sentiment": {
                        "overall_sentiment": sentiment_data.overall_sentiment,
                        "confidence": round(sentiment_data.overall_confidence, 4),
                        "polarity": round(sentiment_data.sentiment_polarity, 4)
                    }
                })

                
                if idx % 10 == 0:
                    print(f"analyzed {idx}/{len(reviews)} reviews")

            except Exception as inner_error:
                #log the specific error for this review
                print(f"  ERROR analyzing review {review.review_id}: {type(inner_error).__name__}: {str(inner_error)}")
                import traceback
                traceback.print_exc()
                #continue with other reviews but include this error in results
                results.append({
                    "review_id": review.review_id,
                    "review_text": review.review[:200] + "..." if len(review.review) > 200 else review.review,
                    "rating": review.rating,
                    "reviewer_name": review.reviewer_name,
                    "sentiment": {
                        "error": f"{type(inner_error).__name__}: {str(inner_error)}"
                    }
                })

        return json.dumps({
            "sentiments": results,
            "total_analyzed": len(results),
            "review_ids": [r.review_id for r in reviews],
            "summary": {
                "positive": sum(1 for r in results if r["sentiment"]["overall_sentiment"] == "Positive"),
                "negative": sum(1 for r in results if r["sentiment"]["overall_sentiment"] == "Negative"),
                "neutral": sum(1 for r in results if r["sentiment"]["overall_sentiment"] == "Neutral"),
                "avg_polarity": round(sum(r["sentiment"]["polarity"] for r in results) / len(results), 4) if results else 0
            }
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Failed to analyze sentiment: {str(e)}",
            "sentiments": [],
            "total_analyzed": 0
        })
