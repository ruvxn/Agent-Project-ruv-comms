from langchain_core.messages import HumanMessage, AIMessage
from src.backend.agent.Agent import Agent
import aiosqlite
import logging
from typing import Any, List
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

class ChatManager:
    def __init__(self, name: str):
        self.messages = []
        self.agent = Agent
        self.graph = None
        self.connection = None
        self.websocket = None
        self.name = name
    async def setup(self, tools: List[Any], description: str):
        logging.info("ChatManager setup")
        self.agent = Agent(tools=tools, name=self.name, description=description)
        self.connection = await aiosqlite.connect(f'src/backend/db/{self.name}.db')
        self.graph = await self.agent.graph_builder(self.connection)

    def load_message(self, messages) -> list:
        for message in messages["messages"]:
            if isinstance(message, HumanMessage):
                if message.content:
                    self.messages.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                if message.content:
                    self.messages.append({"role": "agent", "content": message.content})
            else:
                continue

    async def run_agent(self, user_input):
        try:
            input_to = {"messages": [HumanMessage(content=user_input)]}
            final_state = await self.graph.ainvoke(input = input_to,
                                                   config={"configurable": {"thread_id": "3"}})
            msg = final_state["messages"][-1].content
            self.messages.append({"role": "agent", "content": msg})
            logging.info(f"Agent output {msg}")
        except Exception as e:
            logging.error(e)
        finally:
            logging.info("Agent finished")







