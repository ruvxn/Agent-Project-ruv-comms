from langchain_core.messages import HumanMessage, AIMessage
from common.agent.Agent import Agent
import aiosqlite
from typing import List, Any
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

class ChatManager:
    def __init__(self, name: str):
        self.messages = []
        self.agent = None
        self.graph = None
        self.connection = None
        self.websocket = None
        self.name = name
    async def setup(self, tools: List[Any], prompt: str, type: str):
        logging.info("ChatManager setup")
        if type == "web":
            self.agent = Agent(tools=tools, name=self.name, prompt=prompt)
            self.connection = await aiosqlite.connect(f'db/{self.name}.db')
            self.graph = await self.agent.graph_builder(self.connection)
        elif type == "classify":
            # Import ReviewAgent only when needed to avoid circular imports
            import sys
            import os
            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
            from agents.classification_agent.src.agent.agent_graph import ReviewAgent

            self.agent = ReviewAgent(name=self.name, tools=tools)
            self.connection = await aiosqlite.connect(f'db/{self.name}.db')
            self.graph = await self.agent.build_graph(self.connection)

    def load_message(self, messages):
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







