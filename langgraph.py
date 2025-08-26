from langgraph.prebuilt import create_react_agent

def get_weather(city: str) -> str:
    return f"Its always sunny {city}!"

agent = create_react_agent(
    model="gpt-4o-mini",
    tools=[get_weather],
    prompt="You are a helpful assistant"
)

agent.invoke(
    {"messages":[{"role": "user", "content": "what is the weather in sf"}]}
)