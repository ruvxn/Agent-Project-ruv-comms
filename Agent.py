from AgentState import State
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode
from typing_extensions import List, Any


class Agent:
    """An Agent class"""
    def __init__(self, tools: List[Any]):
        """init method for class Agent requires tools as a list of tools"""
        self.llm = init_chat_model("openai:gpt-4o-mini")
        self.config = {"configurable": {"thread_id": "1"}}
        self.tools = tools
        self.llm_with_tools  = self.llm.bind_tools(self.tools)
        self.graph = self.graph_builder()

    def run(self, user_input: str):
        """Method to run the agent/interact with the agent requires user input"""
        
        for event in self.graph.stream(
                {"messages": [{"role": "user", "content": user_input}]},
                config=self.config
        ):
            for value in event.values():
                return value["messages"][-1].content
                
    def chat(self, state: State):
        return {"messages":[self.llm_with_tools.invoke(state["messages"])]}

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

        tool_node = ToolNode(tools=self.tools)
        graph_builder.add_node("tools", tool_node)

        graph_builder.add_conditional_edges(
            "chatbot",
            self.route_tools,
            {"tools": "tools", "__end__": END},
        )
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.add_edge(START, "chatbot")

        memory = InMemorySaver()
        graph = graph_builder.compile(checkpointer=memory)
        return graph