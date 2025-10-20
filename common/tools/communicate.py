from langchain_core.tools import BaseTool
import asyncio
import logging
from pydantic import BaseModel, Field, create_model, PrivateAttr
from enum import Enum
from common.ConnectionManager import ConnectionManager
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')





class Communicate(BaseTool):
    """Tool class that inherits from base tool"""
    name: str = "ContactOtherAgents"
    description: str = "A tool that allows you to contact other agents given a message, sender and recipient"
    args_schema: type[BaseModel]

    web_connection: ConnectionManager = Field(exclude=True)

    def _run(self, sender_id: str, recipient_id: str, message: str):
        return self._arun(sender_id, recipient_id, message)

    async def _arun(self, sender_id, recipient_id: str, message: str):
        logging.info(f"ARUN id: {recipient_id}")
        logging.info(f"Web connection id: {self.web_connection.agent_id}")
        message_to_send = {
            'message_type': 'message',
            'recipient_id': recipient_id,
            'sender_id': sender_id,
            'message': message

        }
        try:
            await self.web_connection.send(message_to_send, recipient_id)
        except Exception as e:
            logging.error(f"Failed to connect: {e}")
            return



def create_comm_tool(id:str, connection: ConnectionManager) -> Communicate:

    if id == "DirectoryAgent":
        CommunicateInput = create_model(
            f"{id} CommunicateInput",
            message = (str, Field(description="The content of the message to send.")),
            recipient_id = (str, Field(description="The recipient ID of the agent to contact, if you don't have information on the agent id of any other agent, "
                                                   "you may contact 'DirectoryAgent' which can help with finding other agents in the network")                        ),
            sender_id = (str, Field(description="Your own id")),
        )
    else:
        CommunicateInput = create_model(
            f"{id} CommunicateInput",
            message=(str, Field(description="The content of the message to send.")),
            recipient_id=(str, Field(
                description="The recipient ID of the agent to contact, if you don't have information on the agent id you can use your tools")),
            sender_id=(str, Field(description="Your own id")),
        )

    tool = Communicate(
        args_schema=CommunicateInput,
        web_connection=connection,
    )
    return tool

