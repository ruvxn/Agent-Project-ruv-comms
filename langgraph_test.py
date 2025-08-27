from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore
from langmem import create_manage_memory_tool, create_search_memory_tool
def get_weather(city: str) -> str:
    """Get Weather for a given city"""
    return f"Its always sunny {city}!"

store = InMemoryStore(
    index={
        "dims": 1536,
         "embed": "openai:text-embedding-3-small",
    }
)

agent = create_react_agent(
    model="gpt-4o-mini",
    tools=[
        create_manage_memory_tool(namespace=("memories",)),
        create_search_memory_tool(namespace=("memories",))
        ],
    store=store,
    prompt="You are a helpful assistant"
)

while True:
    print("enter your request")
    user_input = input()
    if user_input:
        reply = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]}
        )
        user_input = ""
        print(reply["messages"][-1].content)



