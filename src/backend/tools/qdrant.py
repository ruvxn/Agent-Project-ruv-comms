from langchain_core.tools import BaseTool
import logging
from pydantic import BaseModel, create_model, Field
from typing import Any, Literal, List
import os
from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance
from openai import OpenAI
from enum import Enum

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

def get_embedding(description: str) -> list[float]:
    """Get embedding for directory"""
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    model = "text-embedding-3-small"
    response = client.embeddings.create(
        model=model,
        input=description,
    )

    embeddings = response.data[0].embedding
    if not embeddings or len(embeddings) == 0:
        msg = "No embeddings returned from OpenAI."
        raise ValueError(msg)

    return list(embeddings)



def _check_for_duplicates(collection_name: str,client: QdrantClient, vector: list) -> str | None:
    search_result = client.query_points(
        collection_name=collection_name,
        limit=1,
        query=vector,
        score_threshold=0.90,
    ).points

    if search_result:
        return search_result[0].id
    else:
        return None

def store(data: dict, collection_name: str) -> str:
        client =  QdrantClient()
        if not client.collection_exists(collection_name=collection_name):
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
        vector = get_embedding(data["description"])
        duplicate_check = _check_for_duplicates(collection_name=collection_name, client=client, vector=vector)
        if duplicate_check is None:
            id = data["id"]
            re = "Entry saved successfully"
        else:
            id = duplicate_check
            re = "Existing entry updated successfully"

        client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=id,
                    vector=vector,
                    payload=data,
                )
            ]
        )
        return re



class AgentRegistrationInput(BaseModel):
    """Input schema for the RegisterAgent tool."""
    agent_id: str = Field(
        description="The unique, machine-readable ID for the agent."
    )
    description: str = Field(
        description="A detailed natural language description of the agent's functions and specialities"
    )
    capabilities: List[str] = Field(
        description="A list of the agents capabilities."
    )
    status: Literal["AVAILABLE", "BUSY", "OFFLINE"] = Field(
        description="The current operational status of the agent."
    )

class RegisterAgent(BaseTool):
    """Tool class that inherits from base tool"""
    name: str = "SaveInformationOnOtherAgents"
    description: str = "A tool that allows you to save agent information in a database"
    args_schema: type[BaseModel] = AgentRegistrationInput
    def _run(self,
             agent_id: str,
             description: str,
             capabilities: List[str],
             status: Literal["AVAILABLE", "BUSY", "OFFLINE"]
             ) -> str:
        data = {
            "agent_id": agent_id,
            "description": description,
            "capabilities": capabilities,
            "status": status
        }
        result = store(data=data, collection_name="AgentDirectory")
        return result









