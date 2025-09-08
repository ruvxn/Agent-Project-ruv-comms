from langchain_core.tools import BaseTool
from ddgs import DDGS
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
class WebScrape(BaseTool):
    """A tool that scrapes a website given the link"""
    name: str = "WebScrape"
    description: str = "A tool that can scrape a website given a specific link"
    def _run(self, link: str) -> str:
        return "Link is broken at the moment"
        driver = webdriver.Firefox()
        try:
            driver.get(link)
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "BC4Pbi Juh2_H GPUVdP"))
            )
            return json.dumps(element, indent=2)
        except Exception as e:
            return f'An error occured during scraping: {e}'
class WebSearch(BaseTool):
    """Tool class that inherits from base tool"""
    name: str = "WebSearch"
    description: str = "A tool that can search the web"

    def _run(self, query: str) -> str:
        try:
            with DDGS() as search:
                result = list(search.text(query, max_results=3))
            if not result:
                return "no results found"
            return json.dumps(result, indent=2)
        except Exception as e:
            return f'An error occurred during the search: {e}'
