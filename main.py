from Agent import Agent
from tool import WebScrape, WebSearch
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
            agent_reply = web_agent.run(user_input=user_input)
            print('================================ Human Message =================================')
            print(agent_reply)
        except:
            print("An error occured")
            break

if __name__ == "__main__":
    main()
