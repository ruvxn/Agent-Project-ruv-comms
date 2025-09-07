from AgentState import State
from langgraph.graph import StateGraph, START, END
from tool import TestTool
from Tools import BasicToolNode
import os
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
class Agent:
    def __init__(self):
        self.llm = init_chat_model("openai:gpt-4o-mini")
        #self.tool = TestTool()
        #self.tools = [self.tool]
        #self.llm_with_tool  = self.llm.bind_tools(self.tool)
    def chat(self, state: State):
        return {"messages":[self.llm.invoke(state["messages"])]}
    def route_tools(self, state: State):
        if isinstance(state, list):
            ai_message = state[-1]
        elif messages := state.get("messages", []):
            ai_message = messages[-1]
        else:
            raise ValueError(f'No messages found in input state to tool_edge:{state}')
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return END

    def graph_builder(self):
        graph_builder = StateGraph(State)
        graph_builder.add_node("chatbot", self.chat)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", END)

        #tool_node = BasicToolNode(tools=[self.tools])
        #graph_builder.add_node("tools", tool_node)
        """graph_builder.add_conditional_edges(
            "chatbot",
            self.route_tools,
            {"tools": "tools", END: END},
            )"""
        #graph_builder.add_edge("tools", "chatbot")
        #graph_builder.add_edge(START, "chatbot")
        #conn = sqlite3.connect("test.sqlite")
        memory = InMemorySaver()
        graph = graph_builder.compile(memory)
        return graph