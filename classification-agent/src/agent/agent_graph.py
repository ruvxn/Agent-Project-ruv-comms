from typing import Literal
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite

from langchain_core.messages import ToolMessage

from src.config import (
    ANTHROPIC_API_KEY,
    AGENT_MODEL,
    AGENT_TEMPERATURE,
    AGENT_CHECKPOINT_DB,
    AGENT_VERBOSE
)
from src.agent.agent_state import ReviewAgentState
from src.agent.prompts import get_system_prompt
from src.agent.tools import (
    classify_review_criticality,
    analyze_review_sentiment,
    log_reviews_to_notion,
    get_current_datetime
)


def create_tool_node(tools: list):
    
    tools_by_name = {tool.name: tool for tool in tools}

    def tool_node(state: ReviewAgentState) -> ReviewAgentState:
        """Execute tools and return results"""
        outputs = []
        last_message = state["messages"][-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]

                if AGENT_VERBOSE:
                    print(f"[Tool] Executing {tool_name}...")

        
                tool = tools_by_name[tool_name]
                try:
                    result = tool.invoke(tool_args)
                    if AGENT_VERBOSE:
                        print(f"[Tool] {tool_name} completed successfully")
                except Exception as e:
                    result = f"Error executing {tool_name}: {str(e)}"
                    if AGENT_VERBOSE:
                        print(f"[Tool] {tool_name} failed: {str(e)}")

                #tool message
                tool_message = ToolMessage(
                    content=result,
                    name=tool_name,
                    tool_call_id=tool_id
                )
                outputs.append(tool_message)

        return {"messages": outputs}

    return tool_node


def create_agent_node():
   
    llm = ChatAnthropic(
        model=AGENT_MODEL,
        anthropic_api_key=ANTHROPIC_API_KEY,
        temperature=AGENT_TEMPERATURE,
    )

    #tools at hand
    tools = [
        classify_review_criticality,
        analyze_review_sentiment,
        log_reviews_to_notion,
        get_current_datetime
    ]
    llm_with_tools = llm.bind_tools(tools)

  
    system_prompt = get_system_prompt()

    def agent_node(state: ReviewAgentState) -> ReviewAgentState:
       
        messages = [{"role": "system", "content": system_prompt}] + state["messages"]

        if AGENT_VERBOSE:
            print(f"\n[Agent] Processing {len(state['messages'])} messages")

       
        response = llm_with_tools.invoke(messages)

        if AGENT_VERBOSE:
            if hasattr(response, "tool_calls") and response.tool_calls:
                print(f"[Agent] Calling {len(response.tool_calls)} tools: "
                      f"{[tc['name'] for tc in response.tool_calls]}")
            else:
                print("[Agent] Responding to user (no tools called)")

        return {"messages": [response]}

    return agent_node


def should_continue(state: ReviewAgentState) -> Literal["tools", "end"]:
    """
    this is a conditional edge where claude LLM needs to call tools or respond to user.
    """
    last_message = state["messages"][-1]

    # Check if Claude made tool calls
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    else:
        return "end"


async def build_agent_graph() -> StateGraph:
   
   
    graph = StateGraph(ReviewAgentState)

    #nodes
    agent_node = create_agent_node()
    tool_node = create_tool_node([
        classify_review_criticality,
        analyze_review_sentiment,
        log_reviews_to_notion,
        get_current_datetime
    ])

    #add nodes
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    #add edges
    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    graph.add_edge("tools", "agent")  # loop back after tool call

    return graph


#compile graph with SQLite checkpointing
async def create_agent_app():

    graph = await build_agent_graph()

    # Set up SQLite checkpointing for conversation memory
    # Create aiosqlite connection and initialize AsyncSqliteSaver
    conn = await aiosqlite.connect(AGENT_CHECKPOINT_DB)
    memory = AsyncSqliteSaver(conn)

    # Setup tables if they don't exist
    await memory.setup()

    if AGENT_VERBOSE:
        print(f"[Agent] Initialized with checkpointing to: {AGENT_CHECKPOINT_DB}")

    return graph.compile(checkpointer=memory)



