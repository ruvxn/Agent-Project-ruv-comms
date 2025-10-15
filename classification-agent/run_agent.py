import sys
import argparse
import uuid
from typing import Optional

from src.agent.agent_graph import agent_app


def print_banner():
    """welcome banner"""
    print("\n" + "=" * 70)
    print("  REVIEW CLASSIFICATION AGENT")
    print("=" * 70 + "\n")


def format_message(message) -> str:
    """
    Format a message for display.
    """
    content = getattr(message, "content", "")

    #handle tool calls
    if hasattr(message, "tool_calls") and message.tool_calls:
        tool_info = []
        for tc in message.tool_calls:
            tool_name = tc.get("name", "unknown")
            tool_info.append(f"  -> Calling tool: {tool_name}")
        return "\n".join(tool_info)

    # Handle ToolMessage
    if hasattr(message, "name") and message.name:
        # not displaying raw tool messages they are handled by the agent
        return None

    #regular message content
    return content if content else None


def get_agent_response(messages: list) -> str:
    """
    Extract the final agent response from message history.
    """
    #find last AI message
    for message in reversed(messages):
        # Check if its an AI message 
        if hasattr(message, "content") and message.content:
            #skip if its a tool call without content
            if hasattr(message, "tool_calls") and message.tool_calls:
                continue
            # skip if its a tool message
            if hasattr(message, "name") and message.name:
                continue
            #this is the agents response
            return message.content

    return "(No response)"


def run_interactive_session(thread_id: Optional[str] = None):
    """
    run an interactive session
    """
    # Generate or use provided thread ID
    if not thread_id:
        thread_id = f"session_{uuid.uuid4().hex[:8]}"

    print_banner()
    print(f"Conversation Thread: {thread_id}")
    print(f"(use this ID to resume: python run_agent.py --thread-id {thread_id})\n")

    # Configuration for this conversation
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()

            # Handle special commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye! Your conversation is saved.")
                print(f"Resume with: python run_agent.py --thread-id {thread_id}\n")
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

            response = agent_app.invoke(
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
            print(f"Resume with: python run_agent.py --thread-id {thread_id}\n")
            break

        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again.\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Interactive Review Classification Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_agent.py                              # Start new conversation
  python run_agent.py --thread-id my_session       # Resume conversation

Commands:
  clear    Start new conversation
  exit     Exit the session
        """
    )
    parser.add_argument(
        "--thread-id",
        type=str,
        default=None,
        help="Thread ID to resume a previous conversation"
    )

    args = parser.parse_args()

    # Check for required environment variables
    from src.config import ANTHROPIC_API_KEY
    if not ANTHROPIC_API_KEY:
        print("\nError: ANTHROPIC_API_KEY not set in environment")
        print("Please add your Anthropic API key to the .env file:\n")
        print("ANTHROPIC_API_KEY=sk-ant-api03-your-key-here\n")
        sys.exit(1)

    # Run interactive session
    try:
        run_interactive_session(thread_id=args.thread_id)
    except Exception as e:
        print(f"\nFatal error: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
