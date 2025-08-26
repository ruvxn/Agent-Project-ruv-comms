from smolagents import CodeAgent, LiteLLMModel, DuckDuckGoSearchTool
import os


model = LiteLLMModel(
    model_id="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY")
)
model1 = LiteLLMModel(
    model_id='ollama/gpt-oss',
    api_key='"http://localhost:11434"'
)
agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=model)

print("Hello there enter your question")



while True:
    user_input = input()
    if user_input:
        result = agent.run(user_input)
        user_input = ""
        print(result)

