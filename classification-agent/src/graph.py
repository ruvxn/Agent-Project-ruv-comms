import os
import hashlib
from typing import List, Tuple
from langgraph.graph import Graph

from src.config import DATA_PATH, OLLAMA_MODEL
from src.nodes.load_reviews import load_reviews
from src.database import load_unprocessed_reviews, mark_reviews_processed, get_processing_stats
from src.nodes.detect_errors import detect_errors_with_ollama
from src.nodes.normalize import normalize
from src.utils import RawReview, DetectedError, EnrichedError
from src.nodes.notion_logger import upsert_enriched_error


def _sha12(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]



def build_graph() -> Graph:
    g = Graph()

    def n_load(_: dict) -> List[RawReview]:
        use_db = os.getenv("USE_DATABASE", "false").lower() == "true"

        if use_db:
            #proccessed vs unporcessed stats
            stats = get_processing_stats()
            print(f" Processing stats: {stats['unprocessed']} unprocessed / {stats['total']} total reviews")

            #load unprocessed reviews
            data = load_unprocessed_reviews()

            if not data:
                print("All reviews are up to date")
                return []
        #DB ERR FALLBACK TO CSV
        else:
            data = load_reviews(DATA_PATH)
            data = data[511:] 
            print(f"Loaded {len(data)} reviews from CSV")

        return data

    #detect errors with LLM
    def n_detect(reviews: List[RawReview]) -> List[Tuple[RawReview, List[DetectedError]]]:
        pairs: List[Tuple[RawReview, List[DetectedError]]] = []
        for r in reviews:
            errs = detect_errors_with_ollama(r, OLLAMA_MODEL)
            pairs.append((r, errs))
        return pairs

    #normalise and classify based on severity
    def n_normalize(pairs: List[Tuple[RawReview, List[DetectedError]]]) -> List[EnrichedError]:
        out: List[EnrichedError] = []
        for r, errs in pairs:
            out.extend(normalize(r, errs))
        return out

    #write to Notion and mark as processed
    def n_tee(items: List[EnrichedError]) -> List[EnrichedError]:
        if not items:
            return items

        dry = os.getenv("NOTION_DRY_RUN", "0") in ("1", "true", "True")
        use_db = os.getenv("USE_DATABASE", "false").lower() == "true"
        processed_review_ids = []

        for i, e in enumerate(items, 1):
            hash_value = getattr(e, "error_hash", None) or _sha12(
                f"{e.review.review_id}|{e.error.error_summary}"
            )
            if dry:
                print(f"[dry-run] Would upsert {e.review.review_id} | {e.error.error_summary} | {hash_value}")
            else:
                upsert_enriched_error(e)

            #review IDs for batch processing
            if use_db:
                processed_review_ids.append(e.review.review_id)

            if i % 20 == 0:
                print(f"… processed {i} rows")

        #mark all reviews as processed in batch
        if use_db and processed_review_ids:
            mark_reviews_processed(processed_review_ids)

       
        return items

    # Nodes
    g.add_node("load", n_load)
    g.add_node("detect", n_detect)
    g.add_node("normalize", n_normalize)
    g.add_node("tee", n_tee)

    # Edges 
    g.add_edge("load", "detect")
    g.add_edge("detect", "normalize")
    g.add_edge("normalize", "tee")

    # Entry & finish
    g.set_entry_point("load")
    g.set_finish_point("tee")

    return g


# export workflow for run.py
wf = build_graph().compile()
