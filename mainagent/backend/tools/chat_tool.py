from dotenv import load_dotenv
from ollama import chat
from langchain_core.messages import AIMessage, HumanMessage
import os
import streamlit
from mainagent.backend.model.states.GraphState import GraphState
from mainagent.backend.model.states.tool_state.ToolReturnClass import ToolReturnClass
from mainagent.backend.tools.base_tool import BaseTool
from mainagent.backend.utils import get_user_input, log_decorator

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")


@log_decorator
class chat_tool(BaseTool):
    """Respond to user queries"""

    def invoke(self, arg: dict) -> ToolReturnClass:
        user_input = get_user_input()
        state: GraphState = arg["state"]

        if user_input:
            response = chat(
                OLLAMA_MODEL, [{"role": "user", "content": user_input}])

        state.messages.append(AIMessage(content=response.message.content))

        return ToolReturnClass(
            state=state,
            agent_response=state.messages.ai_response_list[-1].content if state.messages.ai_response_list else "No response",
            meta={"tool_name": "chat_tool"}
        )
