import json
import os
from ollama import Tool, chat
import dotenv
from Controller.utils import extract_first_json

from Model.DTO.JSONResponseDTO import JSONResponseDTO

dotenv.load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")


@Tool
def summary_agent(review_entry: str) -> dict:
    """Add Summary and Tags for Each Review Entity"""

    llm_prompt = f"""
            Return ONLY JSON, nothing else.
            Summarize this user review in 1-2 sentences and
            extract key tags (pros and cons for the product or service or company).
            Respond strictly in JSON with keys 'summary' and 'tags'
            (tags should be a list of string).

            Review:
            {review_entry}
            """

    response = chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": llm_prompt}]
    )
    raw_content = response.message.content

    try:
        return json.loads(raw_content)
    except json.JSONDecodeError:
        return extract_first_json(raw_content)


def get_summarize_reviews_with_ollama(review_entries: list) -> list:
    summarized_reviews, errorList = [], []

    for entry in review_entries:
        try:
            result = summary_agent(
                entry["review"])

            summarized_reviews.append({
                "summary": result["summary"],
                "tags": result["tags"],
            })

        except Exception as e:
            errorList.append((entry["review"], str(e)))

    if len(errorList) == 0:
        json_response_DTO = JSONResponseDTO(
            success=True, data=summarized_reviews, message="summarize_reviews_with_ollama() successful")
    else:
        json_response_DTO = JSONResponseDTO(
            success=False, data=errorList, message="summarize_reviews_with_ollama() fail")

    return json_response_DTO
