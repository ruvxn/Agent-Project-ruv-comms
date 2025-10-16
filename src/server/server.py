import asyncio
import websockets
import json
import logging

from websockets import ConnectionClosedOK
from websockets.client import ClientConnection
from websockets.exceptions import ConnectionClosed, ConnectionClosedError


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

class AgentServer:
    def __init__(self):
        self.agent_registry = {}
        self.queue = asyncio.Queue(maxsize=1000)
        logging.info("Agent server started.")
    async def unregister_agent(self, agent_id:str):
        if agent_id in self.agent_registry:
            del self.agent_registry[agent_id]
            logging.info(f"Agent {agent_id} was unregistered.")
    async def register_agent(self, agent_id:str, websocket: ClientConnection):
        self.agent_registry[agent_id] = websocket
        logging.info(f"Agent {agent_id} was registered.")
        await websocket.send(json.dumps({"status": "registered"}))

    async def forward_message(self, sender_id: str, recipient_id: str ,message:str):
        recipient_ws = self.agent_registry.get(recipient_id)
        if recipient_ws:
            try:
                await recipient_ws.send(json.dumps({
                    "sender": sender_id,
                    "message": message,
                }))
                logging.info(f"Agent {sender_id} sent a message to {recipient_id}.")
            except ConnectionClosedError:
                logging.warning(f"Agent {sender_id} sending {message} failed")
        else:
            logging.warning(f"Agent {sender_id} sending {message} failed")

    async def dispatch_message(self):
        while True:
            try:
                recipient_id, sender_id, message = await self.queue.get()
                await self.forward_message(sender_id, recipient_id, message)
                self.queue.task_done()
            except Exception as e:
                logging.error(f"Error sending message: {e}")

    async def connection_handler(self, websocket):
            logging.info("A client connected")
            agent_id = None

            try:
                registration_message = await websocket.recv()
                data = json.loads(registration_message)
                if data.get("type") == "register" and "id" in data:
                    agent_id = data["id"]
                    self.agent_registry[agent_id] = websocket
                    logging.info(f"Agent {agent_id} registered.")
                    await websocket.send(json.dumps({"status": "registration successful"}))
                else:
                    await websocket.close(1008, json.dumps({"status": "registration failed"}))
                    return
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        recipient_id = data.get("recipient_id")
                        sender_id = data.get("sender_id")
                        message = data.get("message")
                        if recipient_id and message:
                            item = (recipient_id, sender_id, message)
                            logging.info(f"Agent {sender_id} sending {message}")
                            await self.queue.put(item)
                            #await websocket.send(json.dumps({"status": "message sent, please wait for an update from the other agent on the outcome"}))
                        else:
                            #await websocket.send(json.dumps({"status":"Invalid message format"}))
                            logging.error(f"Invalid message format: {message}")
                    except Exception as e:
                        logging.error(f"Error sending message: {e}")
            except ConnectionClosedError:
                logging.info(f"Connection closed for agent {agent_id} (normal closure)")
            except ConnectionClosedOK:
                logging.info(f"Connection closed for agent {agent_id} (normal closure)")
            except Exception as e:
                logging.error(f"Connection handler error for agent {agent_id} : {e}")
            finally:
                if agent_id is not None:
                    await self.unregister_agent(agent_id)

    async def startup(self):
        logging.info("Server Started startup")
        asyncio.create_task(self.dispatch_message())

async def main():
    server = AgentServer()
    await server.startup()
    async with websockets.serve(server.connection_handler, "localhost", 8765):
        logging.info("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

