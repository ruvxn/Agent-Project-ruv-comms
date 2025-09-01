from langgraph.prebuilt import create_react_agent
from langgraph.store.sqlite import SqliteStore
from langgraph.store.memory import InMemoryStore
import sqlite3
from langmem import create_manage_memory_tool, create_search_memory_tool
def get_weather(city: str) -> str:
    """Get Weather for a given city"""
    return f"Its always sunny {city}!"
conn = sqlite3.connect('databse.sqlite')
store = SqliteStore(
    conn=conn,
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
    print("Enter your request")
    user_input = input()
    print(f'User: {user_input}')
    if user_input:
        reply = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]}
        )
        user_input = ""
        print(f'Agent: {reply["messages"][-1].content}')



