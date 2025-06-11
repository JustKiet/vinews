from vinews.core.models import Article, Homepage
from typing import Protocol

class IVinewsScraper(Protocol):
    def fetch(self, url: str) -> str:
        """
        Fetches a page from the given URL.

        :param url: The URL of the page to fetch.
        :type url: str
        :return: A string containing the HTML content of the page.
        :rtype: str
        :raises ValueError: If the provided URL does not start with the base URL.
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        """
        ...

    def scrape_article(self, article_url: str) -> Article:
        """
        Scrapes an article from the given URL.

        :param article_url: The URL of the article to scrape.
        :type article_url: str
        :return: An Article object containing the parsed article data.
        :rtype: Article
        :raises ValueError: If the provided URL does not start with the base URL.
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the article is missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the article contains unexpected elements.
        """
        ...

    def scrape_homepage(self) -> Homepage:
        """
        Scrapes the homepage and returns a structured Homepage object.

        :return: A Homepage object containing the parsed data.
        :rtype: Homepage
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the homepage is missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the homepage contains unexpected elements.
        """
        ...

class AsyncIVinewsScraper(Protocol):
    async def async_fetch(self, url: str) -> str:
        """
        Asynchronously fetches a page from the given URL.

        :param url: The URL of the page to fetch.
        :type url: str
        :return: A string containing the HTML content of the page.
        :rtype: str
        :raises ValueError: If the provided URL does not start with the base URL.
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        """
        ...

    async def async_scrape_article(self, article_url: str) -> Article:
        """
        Asynchronously scrapes an article from the given URL.

        :param article_url: The URL of the article to scrape.
        :type article_url: str
        :return: An Article object containing the parsed article data.
        :rtype: Article
        :raises ValueError: If the provided URL does not start with the base URL.
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the article is missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the article contains unexpected elements.
        """
        ...

    async def async_scrape_homepage(self) -> Homepage:
        """
        Asynchronously scrapes the homepage and returns a structured Homepage object.

        :return: A Homepage object containing the parsed data.
        :rtype: Homepage
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the homepage is missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the homepage contains unexpected elements.
        """
        ...
        