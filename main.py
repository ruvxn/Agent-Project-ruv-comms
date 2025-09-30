import sqlite3
from src.agent.Agent import Agent
from src.tools.tool import WebScrape, WebSearch
from langchain_core.messages import HumanMessage

def show_thinking(agent: Agent, user_input: str):
    """
    Streams the agent's execution process, printing the output of each node as it runs.
    """
    graph = agent.graph_builder()
    config = {"configurable": {"thread_id": "2"}}
    input = {"messages":[HumanMessage(content=user_input)]}

    print("\n--- Agent Start ---")


    for event in graph.stream(
            input,
            config=config,
            stream_mode="updates"
    ):

        for node_name, value in event.items():

            print(f"\n> Executing Node: '{node_name}'")
            if "messages" in value:
                print(" -Messages:")
                for message in value["messages"]:
                    message.pretty_print()
                other_data = {k: v for k, v in value.items() if k != "messages"}
                if other_data:
                    print(f"  - State Updates:\n")
                    for key, val in other_data.items():
                        print(f"{key}: {val}")

    print("\n--- Agent Finished ---\n")




def main():
    websearch = WebSearch()
    webscrape = WebScrape()
    #semanticmemorysearch = SemanticMemorySearch()

    tools = [webscrape, websearch]

    web_agent = Agent(tools=tools, name="WebAgent")
    while True:
        try:
            print('================================ Human Message =================================')
            user_input = input(">>> ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            show_thinking(agent=web_agent, user_input=user_input)
            #result = web_agent.run(user_input=user_input)
            #print(result)
        except Exception as e:
            print(f"An error occurred: {e}")
            break
if __name__ == "__main__":
    main()