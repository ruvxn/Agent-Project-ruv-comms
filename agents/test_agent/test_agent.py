import websockets
import asyncio
import json
import logging
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from common.tools.databse import DatabaseTool
from common.tools.communicate import create_comm_tool
from common.ConnectionManager import ConnectionManager
from common.ChatManager import ChatManager
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


class AgentManager():
    """Manages the agent, however needs to be replaced by the AgentManager
    class from the common directory to reduce duplicate code"""
    def __init__(self):
        self.chat_manager = ChatManager(name="DatabaseAgent")
        self.connection_manager = ConnectionManager(
            agent_id="DatabaseAgent",
            description="An agent that specializes in everything database related",
            capabilities=["DatabaseInsertion"])
        self.task_queue = asyncio.Queue()
        self.user_input = None

    async def worker(self):
        logging.info("Starting worker thread")
        while True:
            task_data = await self.task_queue.get()
            logging.info(f"Worker thread picked up {task_data}")
            message = ""
            if isinstance(task_data, dict):
                message = f"You have a new message from: {task_data['sender_id']}\n+ Message:{task_data['message']}"
            elif isinstance(task_data, str):
                message = task_data
            else:
                logging.info(f"Incorrect message format")
            await self.chat_manager.run_agent(message)
            self.task_queue.task_done()


    async def message_handler(self, message: dict):
        await self.task_queue.put(message)

    async def messanger(self):
        while True:
            try:
                async with websockets.connect("ws://localhost:8765") as websocket:
                    await websocket.send(json.dumps({
                        "message_type": "register",
                        "id": "DatabaseReceiving",
                    }))
                    registration_response = await websocket.recv()
                    logging.info(f"Received registration response: {registration_response}")
                    async for message in websocket:
                        message = json.loads(message)
                        await self.task_queue.put(message)
            except (websockets.exceptions.ConnectionClosedError, ConnectionResetError) as error:
                logging.error(f"Connection closed because: {error}")
                await asyncio.sleep(5)
            except Exception as error:
                logging.error(f"Unexpected error: {error}")
                await asyncio.sleep(5)

    async def startup(self):
        try:
            await self.connection_manager.connect()
        except Exception as e:
            logging.error(f"Failed to connect: {e}")
            return
        await self.connection_manager.start_listening(message_handler=self.message_handler)

        communicate = create_comm_tool("DatabaseAgent", self.connection_manager)
        database = DatabaseTool()
        # memory = MemoryTool()  # must have qdrant running to use this otherwise it will break the code
        tools = [database, communicate]
        description = (
            f"You are the {self.chat_manager.name} agent. Your goal is to help other agents by executing tasks they send you.\n\n"
            "Your workflow:\n"
            "1.  **Receive a Task**: Your primary trigger is an incoming message from another agent.\n"
            "2.  **Execute the Task**: Use your available tools (e.g., database search, calculations) to fulfill the request in the message.\n"
            "3.  **Formulate a Reply**: Once you have the result from your tools, prepare a clear and concise message containing the answer.\n"
            "4.  **Reply to the Sender**: **You MUST always reply.** Use the 'ContactOtherAgents' tool to send the result back to the original agent who contacted you. This is your final step."
        )
        await self.chat_manager.setup(tools=tools, prompt=description, type="web")
        asyncio.create_task(self.worker())


async def main():
    application = AgentManager()
    await application.startup()
    await asyncio.Event().wait()
if __name__ == "__main__":
    asyncio.run(main())