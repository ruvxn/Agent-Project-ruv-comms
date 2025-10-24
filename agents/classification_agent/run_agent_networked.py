"""
Classification Agent with Network Communication Enabled

This script runs the Classification Agent with full multi-agent communication capabilities.
It connects to the AgentServer and can communicate with other agents like DirectoryAgent,
WebAgent, and DatabaseAgent.
"""

import sys
import argparse
import uuid
import asyncio
import os
from typing import Optional

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the base agent
from run_agent import cleanup_terminal, print_banner, format_message, get_agent_response

# Import communication components
from common.ConnectionManager import ConnectionManager
from common.tools.communicate import create_comm_tool


async def run_networked_session(thread_id, graph, connection_manager):
    """
    Run an interactive session with network communication enabled
    """
    # Generate or use provided thread ID
    if not thread_id:
        thread_id = f"session_{uuid.uuid4().hex[:8]}"

    print_banner()
    print(f"NETWORKED MODE - Connected to Agent Network")
    print(f"Conversation Thread: {thread_id}")
    print(f"(use this ID to resume: python run_agent_networked.py --thread-id {thread_id})\n")

    # Configuration for this conversation
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    # Start listening for incoming messages
    task_queue = asyncio.Queue()

    async def message_handler(message: dict):
        """Handle incoming messages from other agents"""
        sender = message.get("sender_id", "Unknown")
        content = message.get("message", "")
        print(f"\n\n[Incoming Message from {sender}]")
        print(f"   {content}")
        # Queue the message to be processed by the agent
        await task_queue.put(f"You have received a message from {sender}: {content}")

    # Start listening for incoming messages
    connection_manager.set_message_handler(message_handler)
    await connection_manager.start_listening()
    asyncio.create_task(process_incoming_messages(task_queue, graph, config))

    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()

            # Handle special commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye! Your conversation is saved.")
                print(f"Resume with: python run_agent_networked.py --thread-id {thread_id}\n")
                cleanup_terminal()
                break

            if user_input.lower() == 'clear':
                thread_id = f"session_{uuid.uuid4().hex[:8]}"
                config["configurable"]["thread_id"] = thread_id
                print(f"\nStarted new conversation: {thread_id}\n")
                continue

            if not user_input:
                continue

            # Invoke the agent
            print("\nAgent: ", end="", flush=True)

            response = await graph.ainvoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config
            )

            # Extract and display the agent's final response
            if response and "messages" in response:
                agent_response = get_agent_response(response["messages"])
                print(agent_response)
            else:
                print("(No response)")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            print(f"Resume with: python run_agent_networked.py --thread-id {thread_id}\n")
            cleanup_terminal()
            break

        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again.\n")


async def process_incoming_messages(queue: asyncio.Queue, graph, config):
    """Process incoming messages from other agents"""
    while True:
        try:
            message = await queue.get()

            # Process the message through the agent
            print("\n\n[Agent processing incoming message...]")
            response = await graph.ainvoke(
                {"messages": [{"role": "user", "content": message}]},
                config=config
            )

            if response and "messages" in response:
                agent_response = get_agent_response(response["messages"])
                print(f"\nAgent Response: {agent_response}\n")

            queue.task_done()
        except Exception as e:
            print(f"\nError processing incoming message: {e}")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Classification Agent with Network Communication",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_agent_networked.py                              # Start new networked conversation
  python run_agent_networked.py --thread-id my_session       # Resume conversation
  python run_agent_networked.py --enable-critique            # Enable self-review loop
  python run_agent_networked.py --enable-memory              # Enable long-term memory

Commands:
  clear    Start new conversation
  exit     Exit the session

Multi-Agent Communication:
  Ask the agent to contact other agents:
  - "Contact DirectoryAgent and ask what agents are available"
  - "Ask WebAgent to search for LangGraph tutorials"
  - "Tell DatabaseAgent to store this review data"
        """
    )
    parser.add_argument(
        "--thread-id",
        type=str,
        default=None,
        help="Thread ID to resume a previous conversation"
    )
    parser.add_argument(
        "--enable-critique",
        action="store_true",
        help="Enable the critique/self-review loop for better quality responses"
    )
    parser.add_argument(
        "--enable-memory",
        action="store_true",
        help="Enable long-term memory (learns from past interactions)"
    )

    args = parser.parse_args()

    # Check for required environment variables
    from src.config import ANTHROPIC_API_KEY
    if not ANTHROPIC_API_KEY:
        print("\nError: ANTHROPIC_API_KEY not set in environment")
        print("Please add your Anthropic API key to the .env file:\n")
        print("ANTHROPIC_API_KEY=sk-ant-api03-your-key-here\n")
        sys.exit(1)

    print("\nConnecting to agent network...")

    # Initialize ConnectionManager
    connection_manager = ConnectionManager(
        agent_id="ClassificationAgent",
        description="An agent that analyzes and classifies customer reviews with sentiment analysis",
        capabilities=["SentimentAnalysis", "CriticalityClassification", "ReviewAnalysis", "NotionLogging"]
    )

    agent_app = None  # Initialize to prevent UnboundLocalError

    try:
        # Connect to the network
        await connection_manager.connect()
        print("Connected to agent network\n")

        # Build and compile the agent graph with communication enabled
        from src.agent.agent_graph import create_agent_app

        agent_app = await create_agent_app(
            enable_critique=args.enable_critique,
            enable_memory=args.enable_memory,
            connection_manager=connection_manager
        )

        print("Agent initialized with multi-agent communication enabled!")

        # Run networked session
        await run_networked_session(
            thread_id=args.thread_id,
            graph=agent_app,
            connection_manager=connection_manager
        )

    except Exception as e:
        print(f"\nFatal error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        cleanup_terminal()
        sys.exit(1)
    finally:
        # Cleanup
        if connection_manager:
            await connection_manager.close()
        if agent_app and hasattr(agent_app, 'checkpointer') and hasattr(agent_app.checkpointer, 'conn'):
            try:
                await agent_app.checkpointer.conn.close()
            except Exception:
                pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        cleanup_terminal()
