from src.agent.Agent import Agent
from src.tools.tool import WebScrape, WebSearch
def main():
    websearch = WebSearch()
    webscrape = WebScrape()
    tools = [webscrape, websearch]
    web_agent = Agent(tools=tools)

    while True:
        try:
            print('================================ Human Message =================================')
            user_input = input()
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            result = web_agent.run(user_input=user_input)
            print('================================ AI =================================')
            print(result)
        except Exception as e:
            print(f"An error occured {e}")
            break

if __name__ == "__main__":
    main()
