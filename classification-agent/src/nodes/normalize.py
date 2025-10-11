from typing import List, Dict, Tuple
from src.utils import RawReview, DetectedError, EnrichedError, SentimentData, Criticality, hash_error
from src.nodes.classify_criticality import classify_criticality


def apply_sentiment_adjustment(
    base_criticality: Criticality,
    sentiment: SentimentData,
    review_rating: int
) -> Tuple[Criticality, bool]:
    """
    Adjust criticality based on sentiment analysis and review rating.

    Args:
        base_criticality: The base criticality from keyword classification
        sentiment: Sentiment analysis data for the review
        review_rating: Customer rating (1-5)

    Returns:
        Tuple of (final_criticality, was_influenced)
    """
    polarity = sentiment.sentiment_polarity
    influenced = False
    final = base_criticality

    # Strong negative sentiment escalation
    if polarity < -0.85 and base_criticality == "Major":
        final = "Critical"
        influenced = True
    elif polarity < -0.70 and base_criticality == "Minor":
        final = "Major"
        influenced = True

    # Low rating escalation (1-2 stars with Major issues → Critical)
    if review_rating <= 2 and base_criticality == "Major":
        final = "Critical"
        influenced = True

    # Strong positive sentiment downgrade (positive review with minor UI issue)
    if polarity > 0.85 and base_criticality == "Minor":
        final = "Suggestion"
        influenced = True

    return final, influenced


#enrich error items with sentiment-aware criticality
def normalize(review: RawReview, detected: List[DetectedError], sentiment: SentimentData) -> List[EnrichedError]:
    """
    Normalize errors with sentiment-aware criticality classification.

    Args:
        review: The original review
        detected: List of detected errors
        sentiment: Sentiment analysis data

    Returns:
        List of enriched errors with deduplicated hashes
    """
    enriched: List[EnrichedError] = []

    for e in detected:
        # Base classification from keywords
        base_crit = classify_criticality(e)

        # Sentiment-adjusted classification
        final_crit, influenced = apply_sentiment_adjustment(
            base_crit,
            sentiment,
            review.rating
        )

        enriched.append(
            EnrichedError(
                review=review,
                error=e,
                criticality=final_crit,
                error_hash=hash_error(review.review_id, e.error_summary),
                sentiment_data=sentiment,  # NEW: Attach sentiment data
                sentiment_influenced_criticality=influenced  # NEW: Track if sentiment changed severity
            )
        )

    # Deduplicate by hash
    uniq: Dict[str, EnrichedError] = {}
    for it in enriched:
        uniq[it.error_hash] = it
    return list(uniq.values())
