from smolagents import CodeAgent, LiteLLMModel
import os


model = LiteLLMModel(
    model_id="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY")
)
model1 = LiteLLMModel(
    model_id='ollama/gpt-oss',
    api_key='"http://localhost:11434"'
)
agent = CodeAgent(tools=[], model=model1)

result = agent.run("calculate the sum of numbers from 1 to 10")
print(result)