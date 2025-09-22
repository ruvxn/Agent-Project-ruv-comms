from langchain_core.tools import BaseTool
from ddgs import DDGS
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing_extensions import override
from langmem import create_memory_manager, create_search_memory_tool
from src.memory.episodic import Episode
from src.memory.semantic import Semantic
class WebScrape(BaseTool):
    """A tool that scrapes a website given the link"""
    name: str = "WebScrape"
    description: str = "A tool that can scrape a website given a link"
    @override
    def _run(self, link: str) -> str:
        allowable_domain = ["https://example.com/", "https://www.productreview.com.au/", "https://www.scorptec.com.au/", "https://www.harveynorman.com.au/", "https://en.wikipedia.org/wiki/"]
        if any(link.startswith(domain) for domain in allowable_domain):
            driver = webdriver.Firefox()
            data_to_return = ""
            review_xpath = f"//div[@class='product-list-wrapper sli_container  ']"
            try:
                driver.get(link)
                elements = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.XPATH, review_xpath))
                )
                data_to_return = (json.dumps(element.text for element in elements))
            except Exception as e:
                return f'An error occurred during scraping: {e}'
            finally:
                driver.quit()
                data_json = json.dumps(data_to_return)
                return data_json
        else:
            return f"{link} is not in the allowable domains to visit"

class WebSearch(BaseTool):
    """Tool class that inherits from base tool"""
    name: str = "WebSearch"
    description: str = "A tool that can search the web"

    @override
    def _run(self, query: str) -> str:
        try:
            with DDGS() as search:
                result = list(search.text(query, max_results=3))
            if not result:
                return "no results found"
            return json.dumps(result, indent=2)
        except Exception as e:
            return f'An error occurred during the search: {e}'

class SemanticMemorySearch(BaseTool):
    name: str ="SemanticMemoryCreator"
    description: str = "Create semantic memory tool"

    @override
    def _run(self, memory: str) -> str:
        search = create_search_memory_tool("memories")
        """
        memories = search.invoke(
            {"messages": memory},
            config={"configurable": {"user_id": "test"}}
        )
        """

        return "no memories found"


