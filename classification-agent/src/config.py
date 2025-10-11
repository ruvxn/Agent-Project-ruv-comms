from dotenv import load_dotenv
import os

load_dotenv()

DATA_PATH = os.getenv("DATA_PATH", "./data/tech_service_reviews_500_with_names_ratings.csv")

# LLM
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Sentiment Analysis Configuration
ENABLE_SENTIMENT = os.getenv("ENABLE_SENTIMENT", "true").lower() in ("true", "1", "yes")
SENTIMENT_MODEL = os.getenv("SENTIMENT_MODEL", "yangheng/deberta-v3-base-absa-v1.1")
SENTIMENT_CONFIDENCE_THRESHOLD = float(os.getenv("SENTIMENT_CONFIDENCE_THRESHOLD", "0.8"))
SENTIMENT_BOOST_THRESHOLD = float(os.getenv("SENTIMENT_BOOST_THRESHOLD", "-0.85"))

# Notion
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

# Anthropic
