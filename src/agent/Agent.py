from langchain_core.messages import HumanMessage
from .AgentState import State
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
        #Shows the final message from the LLM
        input = {"messages": [HumanMessage(content=user_input)]}
        final_state = self.graph.invoke(
            input,
            config=self.config
        )
        return final_state["messages"][-1].content

    def planner(self, state: State):
        planner_messages = state["messages"]+ [
            (
                "system",
                "You are an expert planner, create a concise, step-by-step plan to answer the user's request. Respond with the plan only"
            )
        ]
        plan = self.llm.invoke(planner_messages).content
        state["plan"] = plan

        return state

    def chat(self, state: State):
        system_prompt = (
            "You are a helpful assistant. Your goal is to answer the user's request by following the plan.\n"
            "1. First, decide if you need to call a tool to execute the current step of the plan.\n"
            "2. If you do, call the tool. \n"
            "3. **Crucially, when you receive the result from a tool (a ToolMessage), you MUST use that result to form a final answer for the user.**\n"
            "4. Do NOT call the same tool again unless the plan explicitly requires it for a different step. Once you have the information, give the answer.\n"
            f"\nHere is the plan to follow: {state.get('plan', 'No plan available')}"
        )
        if state.get('critique') and state['critique'] != 'None':
            system_prompt += f"you must revise your previous answer based on the following critique: {state['critique']}"
        messages_with_prompt = [("system", system_prompt)] + state["messages"]
        ai_response = self.llm_with_tools.invoke(messages_with_prompt)
        return {"messages":[ai_response]}

    def critique(self, state: State):
        critique_prompt = (
            "You are an expert critic, review the proposed final answer answer to the original user request."
            "Is the answer complete, accurate, and does it fully address the user's query?"
            "If the answer is good respond with 'yes'."
            "If it needs improvement, provide a concise critique of whats missing or wrong."
        )
        critique_message = [
            state["messages"][0],
            state["messages"][-1],
            ("system", critique_prompt)
        ]

        critique = self.llm.invoke(critique_message).content
        if "yes" in critique.lower():
            return {'critique':'None'}
        else:
            return {'critique': critique}

    def route_tools(self, state: State):
        ai_message = state["messages"][-1]
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return "critique"

    def should_continue(self, state: State):
        if state.get("critique") and state["critique"] != "None":
            return "chatbot"
        else:
            return END

    def graph_builder(self):
        graph_builder = StateGraph(State)
        graph_builder.add_node("planner", self.planner)

        graph_builder.add_node("chatbot", self.chat)
        tool_node = ToolNode(tools=self.tools)
        graph_builder.add_node("tools", tool_node)
        graph_builder.add_node("critique", self.critique)

        graph_builder.add_edge(START, "planner")
        graph_builder.add_edge("planner", "chatbot")
        graph_builder.add_edge("tools", "chatbot")

        graph_builder.add_conditional_edges(
            "chatbot",
            self.route_tools,
            {"tools": "tools", "critique": "critique"},
        )
        graph_builder.add_conditional_edges(
            "critique",
            self.should_continue,
            {"chatbot":"chatbot", "__end__": END}
        )

        memory = InMemorySaver()
        graph = graph_builder.compile(checkpointer=memory)
        return graph