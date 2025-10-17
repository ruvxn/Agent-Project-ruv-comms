from langchain_core.tools import BaseTool
import logging
from pydantic import BaseModel, Field
from typing import Literal, List
import os
from common.stores.ClientStore import ClientStore



class AgentRegistrationInput(BaseModel):
    """Input schema for the RegisterAgent tool."""
    agent_id: str = Field(
        description="The agent id."
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
    name: str = "register_agent"
    description: str = "A tool that allows you to save agent information in a database"
    args_schema: type[BaseModel] = AgentRegistrationInput
    def _run(self,
             agent_id: str,
             description: str,
             capabilities: List[str],
             status: Literal["AVAILABLE", "BUSY", "OFFLINE"]
             ) -> str:
        client = ClientStore()
        data = {
            "agent_id": agent_id,
            "description": description,
            "capabilities": capabilities,
            "status": status
        }
        result = client.store(data=data)
        return ""

