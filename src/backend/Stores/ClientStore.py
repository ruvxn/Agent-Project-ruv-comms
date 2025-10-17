from langchain_core.tools import BaseTool
import logging
from pydantic import BaseModel, create_model, Field
from typing import Any, Literal, List
import os
from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance
from openai import OpenAI
from enum import Enum
from .Embedding import Embedding
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')




class ClientStore():
    def __init__(self, collection_name = "AgentRegistery") -> None:
        self.client = QdrantClient(host="localhost", port=6333)
        self.collection_name = collection_name
        if not self.client.collection_exists(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
        self.embedding = Embedding()

    def _check_for_duplicates(self,vector: List[float]) -> str | None | int:
       
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

    def store(self, data: dict):
            vector = self.embedding.get_embedding(quary=data["description"])
            if not self.client.collection_exists(collection_name=self.collection_name):
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
                )
            check = self._check_for_duplicates(vector=vector)
            if check is None:
                id = data['agent_id']
            else:
                id = check
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=id,
                        vector=vector,
                        payload=data,
                    )
                ]
            )
            
    def get(self, quary: dict) -> dict | None:
        vector = self.embedding.get_embedding(quary["description"])
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            limit=1, 
            query=vector,
            with_payload=True,
            with_vectors=False,
            score_threshold=0.9,
        ).model_dump()

        agent_info = search_result
        return None








