from Agent import Agent

def stream_graph_updates(user_input: str, graph):
    config = {"configurable": {"thread_id": "1"}}
    for event in graph.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config
    ):
        for value in event.values():
            print("================================ Assistant =================================")
            print(value["messages"][-1].content)

def main():
    agent = Agent()
    graph = agent.graph_builder()
    while True:
        try:
            print('================================ Human Message =================================')
            user_input = input()
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            stream_graph_updates(user_input, graph)
        except:
            # fallback if input() is not available
            user_input = "What do you know about LangGraph?"
            print("User: " + user_input)
            stream_graph_updates(user_input, graph)
            break


if __name__ == "__main__":
    main()
