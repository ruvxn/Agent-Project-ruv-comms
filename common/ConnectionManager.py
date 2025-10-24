from typing import List
import websockets
import asyncio
import json
import logging
from websockets import ConnectionClosedError

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
class ConnectionManager:
    def __init__(self, agent_id: str, description: str, capabilities: List[str],):
        self.connection = None,
        self.uri = "ws://localhost:8765"
        self._websocket: websockets.ClientProtocol | None = None
        self.agent_id = agent_id
        self.description = description
        self.capabilities = capabilities
        self.message_handler = None

    async def connect(self):
        try:
            self._websocket = await websockets.connect(self.uri)
            await self._register()
        except websockets.exceptions.ConnectionClosedError:
            logging.info("Connection Closed")
            self.websocket = None
            await asyncio.sleep(5)
        except Exception as e:
            logging.info(f"Error: {e}")
            self._websocket = None
            await asyncio.sleep(5)

    async def _register(self) -> str:
        if not self._websocket:
            raise ConnectionError("Websocket not connected")

        await self._websocket.send(json.dumps({
            "message_type": "register",
            "agent_id": self.agent_id,
            "description": self.description,
            "capabilities": self.capabilities,

        }))
        registration_response = await self._websocket.recv()
        logging.info(registration_response)

    async def send(self, payload):
        logging.info(f"Sending message")
        if not self._websocket:
            logging.error("Websocket not connected")
            return "Websocket not connected"


        await self._websocket.send(json.dumps(payload))

    def set_message_handler(self, message_handler):
        """Set the message handler callback"""
        self.message_handler = message_handler

    async def start_listening(self, message_handler=None):
        if not self._websocket:
            raise ConnectionError("Websocket not connected")
        handler = message_handler or self.message_handler
        if not handler:
            raise ValueError("No message handler provided")
        self.task = asyncio.create_task(self.receive(handler))

    async def receive(self, message_handler):
        while True:
            if self._websocket is None:
                raise ConnectionError
            else:
                try:
                    async with self._websocket as websocket:
                        async for message in websocket:
                            task_data = json.loads(message)
                            logging.info(f"Received message: {task_data}")
                            await message_handler(task_data)
                except (websockets.exceptions.ConnectionClosedError, ConnectionResetError) as error:
                    logging.error(error)
                    self.websocket = None
                    await self.connect()
                    await asyncio.sleep(5)
                except Exception as error:
                    logging.error(f"Error: {error}")
                    self.websocket = None
                    await self.connect()
                    await asyncio.sleep(5)

    async def close(self):
        self._websocket.close()
        self._websocket = None


