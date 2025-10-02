from typing import Any
import os
from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance
from openai import OpenAI
from src.backend.memory.semantic import Semantic
from src.backend.memory.episodic import Episode
from typing import Union

MemoryObject = Union[Semantic, Episode,str]
class Embedding:
    """
    Embedding class for the custom qdrant class, it uses open AI embedding by default
    """
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = "text-embedding-3-small"

    def semantic_to_sentence(self, memory: Semantic):
        """converts semantic memory to sentence representation for embedding"""
        return f"{memory.subject} {memory.predicate} {memory.object}"


    def episodic_to_sentence(self, memory: Episode):
        """converts episodic memory to sentence representation for embedding"""
        return f"{memory.observation} {memory.thoughts} {memory.action} {memory.result}"

    def get_embedding(self, memory: MemoryObject) -> list[float]:
        """Get the embedding for the given memory using openai. expects a memory object which contains
        both semantic and episodic memories
        """
        if isinstance(memory, Semantic):
            text = self.semantic_to_sentence(memory)
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
            )
            # as vector
            embeddings = response.data[0].embedding
            if not embeddings or len(embeddings) == 0:
                msg = "No embeddings returned from OpenAI."
                raise ValueError(msg)

            return list(embeddings)

        elif isinstance(memory, Episode):
            text = self.episodic_to_sentence(memory)
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
            )
            embeddings = response.data[0].embedding
            if not embeddings or len(embeddings) == 0:
                msg = "No embeddings returned from OpenAI."
                raise ValueError(msg)

            return list(embeddings)

        elif isinstance(memory, Semantic):
            response = self.client.embeddings.create(
                model=self.model,
                input=memory,
            )
            embeddings = response.data[0].embedding
            if not embeddings or len(embeddings) == 0:
                msg = "No embeddings returned from OpenAI."
                raise ValueError(msg)

            return list(embeddings)

        elif isinstance(memory, str):
            response = self.client.embeddings.create(
                model=self.model,
                input=memory,
            )
            embeddings = response.data[0].embedding
            if not embeddings or len(embeddings) == 0:
                msg = "No embeddings returned from OpenAI."
                raise ValueError(msg)

            return list(embeddings)
        else:
            raise Exception(f"Unknown memory type: {type(memory)}")



class QdrantStore():
    def __init__(self, collection_name: str):
        self.client = QdrantClient(host="localhost", port=6333)
        self.collection_name = collection_name
        if not self.client.collection_exists(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
        self.embedding = Embedding()

    def get(self, query: str) -> list[dict[str, Any]]:
        """retrieves memories given a query or a text input and returns a list of relevant memories"""
        vector = self.embedding.get_embedding(query)
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            limit=5, #update this to get more relevant memories
            query=vector,
        ).points

        return [result.payload for result in search_result]

    def put(self, memories):
        """Stores the memory, while also checking for duplicate memories"""
        for memory in memories:
            check = self._check_for_duplicates(memory)
            if check is None:
                id = memory.id
            else:
                id = check
            vector = self.embedding.get_embedding(memory.content)
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=id,
                        vector=vector,
                        payload=memory.content.model_dump(),
                    )
                ]
            )

    def _check_for_duplicates(self, memory: MemoryObject) -> str | None:
        """Takes a memory object semantic or episodic memories and checks weather there are any similar
        memories already in the storage"""
        vector = self.embedding.get_embedding(memory.content)

        search_result = self.client.query_points(
            collection_name=self.collection_name,
            limit=1,
            query=vector,
            score_threshold=0.90,
        ).points

        if search_result:
            return search_result[0].id
        else:
            return None




