from langchain_core.tools import BaseTool
from ddgs import DDGS
import json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from typing_extensions import override
from langmem import create_memory_manager, create_search_memory_tool
from src.memory.semantic import Semantic
from src.memory.episodic import Episode
from markdownify import markdownify as md
from readability import Document
from src.memory.QdrantStore import QdrantStore



class WebScrape(BaseTool):
    """A tool that scrapes a website given the link"""
    name: str = "WebScrape"
    description: str = "A tool that can scrape a website given a link"
    @override
    def _run(self, link: str) -> str:
        allowable_domain = ["https://example.com/", "https://www.productreview.com.au/", "https://www.scorptec.com.au/",
                            "https://www.harveynorman.com.au/", "https://en.wikipedia.org/wiki/", "https://au.trustpilot.com/", "https://www.techradar.com/"]
        if any(link.startswith(domain) for domain in allowable_domain):
            driver = webdriver.Firefox()
            try:
                driver.get(link)
                WebDriverWait(driver, 20)
                html_content = driver.page_source
                doc  = Document(html_content)
                title = doc.title()
                body = doc.summary()
                content_md = md(body)
                return f"#{title}\n\n{content_md}"
            except Exception as e:
                return f'An error occurred during scraping: {e}'
            finally:
                driver.quit()
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








