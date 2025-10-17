from langchain_core.tools import BaseTool
import asyncio
import logging
from pydantic import BaseModel, Field, create_model, PrivateAttr
from enum import Enum
from common.ConnectionManager import ConnectionManager
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


ALL_AGENTS = ["Database", "WebAgent"]



class Communicate(BaseTool):
    """Tool class that inherits from base tool"""
    name: str = "ContactOtherAgents"
    description: str = "A tool that allows you to contact other agents given a message, sender and recipient"
    args_schema: type[BaseModel]

    web_connection: ConnectionManager = Field(exclude=True)

    def _run(self, message: str, recipient_id: Enum):
        return self._arun(message, recipient_id)

    async def _arun(self, message: str, recipient_id: Enum):
        logging.info(f"ARUN message: {message}")
        logging.info(f"Web connection id: {self.web_connection.agent_id}")
        try:
            await self.web_connection.send(message, recipient_id.value)
        except Exception as e:
            logging.error(f"Failed to connect: {e}")
            return



def create_comm_tool(id:str, connection: ConnectionManager) -> Communicate:

    available_agents = []
    for agent in ALL_AGENTS:
        if agent.startswith(id):
            continue
        else:
            available_agents.append(agent)

    AVAILABLE_AGENTS = Enum(
        f"{id} AVAILABLE_AGENTS",
        {agent: agent for agent in available_agents}
    )

    CommunicateInput = create_model(
        f"{id} CommunicateInput",
        message = (str, Field(description="The content of the message to send.")),
        recipient_id = (AVAILABLE_AGENTS, Field(description="The recipient ID of the agent to contact.")),
    )

    tool = Communicate(
        args_schema=CommunicateInput,
        web_connection=connection,
    )
    return tool

