from src.agent.Agent import Agent
from src.tools.tool import WebScrape, WebSearch
from langchain_core.messages import HumanMessage



def show_thinking(agent: Agent, user_input: str):
    """
    Streams the agent's execution process, printing the output of each node as it runs.
    """

    config = {"configurable": {"thread_id": "1"}}
    input = {"messages":[HumanMessage(content=user_input)]}
    print("\n--- Agent Start ---")



    for event in agent.graph.stream(
            input,
            config=config,
            stream_mode="updates"
    ):
        for node_name, value in event.items():
            print(f"\n> Executing Node: '{node_name}'")
            if "messages" in value:
                for message in value["messages"]:
                    message.pretty_print()
            elif "plan" in value:
                print(f"  Plan Created: {value['plan']}")
            elif "critique" in value and value['critique'] != 'None':
                print(f"  Critique Received: {value['critique']}")

    print("\n--- Agent Finish ---\n")


def main():
    websearch = WebSearch()
    webscrape = WebScrape()
    tools = [webscrape, websearch]
    web_agent = Agent(tools=tools)
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