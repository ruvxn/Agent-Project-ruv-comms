from dotenv import load_dotenv
from ollama import chat
import os

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
TOP_K = os.getenv("TOP_K")


def chat_agent(role: str, content: str):
    response = chat(OLLAMA_MODEL, [{"role": role, "content": content}])
    return response['message']['content']
