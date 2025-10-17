"""
log to prev notion db tool
tool to log the processed rveiews with the sentiment score and theri sveerirty classification to the notion dtabase
"""

import os
import json
from typing import List
from langchain_core.tools import tool

from src.utils import RawReview, DetectedError, EnrichedError, SentimentData, hash_error
from src.nodes.notion_logger import upsert_enriched_error
from src.database import mark_reviews_processed


def parse_review_data(review_data_json: str) -> List[EnrichedError]:
   
    try:
        data = json.loads(review_data_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")

    enriched_errors = []

    reviews_list = data.get("reviews", [])
    sentiments_list = data.get("sentiments", [])

    #sentiment by review id
    sentiment_map = {}
    for sent_item in sentiments_list:
        review_id = sent_item.get("review_id")
        if review_id and "sentiment" in sent_item:
            s = sent_item["sentiment"]
            sentiment_map[review_id] = SentimentData(
                review_id=review_id,
                overall_sentiment=s.get("overall_sentiment", "Neutral"),
                overall_confidence=s.get("confidence", 0.0),
                sentiment_polarity=s.get("polarity", 0.0)
            )

    for review_item in reviews_list:
        review_id = review_item.get("review_id")
        if not review_id:
            continue

        review = RawReview(
            review_id=review_id,
            review=review_item.get("review_text", ""),
            username=review_item.get("username", ""),
            email=review_item.get("email", ""),
            date=review_item.get("date", ""),
            reviewer_name=review_item.get("reviewer_name", ""),
            rating=review_item.get("rating", 3)
        )

        #get sentiment data
        sentiment_data = sentiment_map.get(review_id)

    
        errors = review_item.get("errors", [])
        for error_item in errors:
            # Support both old and new field names
            categories = error_item.get("categories") or error_item.get("error_type", ["Other"])
            severity = error_item.get("severity") or error_item.get("criticality", "Medium Priority")

            detected_error = DetectedError(
                error_summary=error_item.get("error_summary", ""),
                error_type=categories,  # Maps to categories
                severity=severity,       # LLM-generated severity
                rationale=error_item.get("rationale", "")
            )

            criticality = severity  # Use severity as criticality for EnrichedError

            enriched_errors.append(
                EnrichedError(
                    review=review,
                    error=detected_error,
                    criticality=criticality,
                    error_hash=hash_error(review_id, detected_error.error_summary),
                    sentiment_data=sentiment_data,
                    sentiment_influenced_criticality=False  # Can be enhanced later
                )
            )

    return enriched_errors


@tool
def log_reviews_to_notion(
    review_data: str,
    include_sentiment: bool = True,
    include_criticality: bool = True,
    dry_run: bool = False
) -> str:
    """Log processed reviews to Notion database for team tracking and collaboration."""
    try:
        
        if not os.getenv("NOTION_API_KEY") or not os.getenv("NOTION_DATABASE_ID"):
            return json.dumps({
                "success": False,
                "error": "Notion is not configured. Set NOTION_API_KEY and NOTION_DATABASE_ID in .env file",
                "total_logged": 0
            })

       
        global_dry_run = os.getenv("NOTION_DRY_RUN", "0") in ("1", "true", "True")
        dry_run = dry_run or global_dry_run

        #parse the review data
        enriched_errors = parse_review_data(review_data)

        if not enriched_errors:
            return json.dumps({
                "success": False,
                "message": "No valid review data found to log",
                "total_logged": 0
            })

        #processed tracking
        processed_review_ids = []
        logged_count = 0

        #write to notion
        for enriched_error in enriched_errors:
            if dry_run:
                print(f"[DRY RUN] Would upsert: {enriched_error.review.review_id} | "
                      f"{enriched_error.error.error_summary} | {enriched_error.criticality}")
            else:
                #actually write to Notion
                try:
                    print(f"  Logging {enriched_error.review.review_id} to Notion...")
                    upsert_enriched_error(enriched_error)
                    print(f"  Successfully logged {enriched_error.review.review_id}")
                except Exception as notion_error:
                    print(f"  ERROR logging {enriched_error.review.review_id}: {type(notion_error).__name__}: {str(notion_error)}")
                    import traceback
                    traceback.print_exc()
                    raise  

            logged_count += 1
            if enriched_error.review.review_id not in processed_review_ids:
                processed_review_ids.append(enriched_error.review.review_id)

        #mark reviews as processed in database
        use_db = os.getenv("USE_DATABASE", "false").lower() == "true"
        if use_db and processed_review_ids and not dry_run:
            mark_reviews_processed(processed_review_ids)

        return json.dumps({
            "success": True,
            "total_logged": logged_count,
            "total_reviews": len(processed_review_ids),
            "review_ids": processed_review_ids,
            "dry_run": dry_run,
            "message": f"{'[DRY RUN] Would log' if dry_run else 'Successfully logged'} {logged_count} error(s) from {len(processed_review_ids)} review(s) to Notion"
        }, indent=2)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in log_reviews_to_notion: {type(e).__name__}: {str(e)}")
        print(error_details)
        return json.dumps({
            "success": False,
            "error": f"Failed to log reviews to Notion: {type(e).__name__}: {str(e)}",
            "error_type": type(e).__name__,
            "total_logged": 0
        })
