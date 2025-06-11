from vinews.modules.vnexpress.parsers import VinewsVnExpressArticleParser, VinewsVnExpressPageParser
from vinews.core.interfaces.ivinewsscraper import IVinewsScraper, AsyncIVinewsScraper
from vinews.core.constants import DEFAULT_HEADERS
from vinews.core.utils import VinewsValidator
from vinews.core.models import Article, Homepage
from typing import Any
import tenacity
import httpx

class VinewsVnExpressScraper(IVinewsScraper, AsyncIVinewsScraper):
    def __init__(self, **kwargs: Any):
        self._base_url = "https://vnexpress.net/"
        self._domain = "vnexpress.net"
        self._article_parser = VinewsVnExpressArticleParser()
        self._page_parser = VinewsVnExpressPageParser()

        timeout = kwargs.get("timeout", 10.0)
        timeout_connect = kwargs.get("timeout_connect", 5.0)

        if not isinstance(timeout, (int, float)) or not isinstance(timeout_connect, (int, float)):
            raise ValueError("Timeout values must be numeric (int or float).")
        if timeout <= 0 or timeout_connect <= 0:
            raise ValueError("Timeout values must be greater than 0.")
        if timeout < timeout_connect:
            raise ValueError("Timeout must be greater than or equal to connect timeout.")
        
        self._timeout = httpx.Timeout(
            timeout=timeout, 
            connect=timeout_connect,
        )
        
        headers: dict[str, Any] = kwargs.get("headers", DEFAULT_HEADERS)

        self._headers = headers

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=2, max=10),
        stop=tenacity.stop_after_attempt(5),
        reraise=True,
        retry=tenacity.retry_if_exception_type(httpx.HTTPStatusError)
    )
    def fetch(self, url: str) -> str:
        """
        Fetches a VnExpress page from the given URL.

        :param url: The URL of the page to fetch.
        :type url: str
        :return: A string containing the HTML content of the page.
        :rtype: str
        :raises ValueError: If the provided URL does not belong to the domain (vnexpress.net).
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        """
        if not VinewsValidator.validate_url_with_domain(url, self._domain):
            raise ValueError(f"Invalid URL: {url}. Must belong to domain {self._domain}")

        with httpx.Client(timeout=self._timeout) as client:
            response = client.get(url, headers=self._headers)
            response.raise_for_status()

        return response.text

    def scrape_article(self, article_url: str) -> Article:
        """
        Scrapes a VnExpress article from the given URL.

        :param article_url: The URL of the article to scrape.
        :type article_url: str
        :return: An Article object containing the parsed article data.
        :rtype: Article
        :raises ValueError: If the provided URL does not belong to the domain or is not an HTML page.
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the article is missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the article contains unexpected elements.
        """
        if not VinewsValidator.validate_url_with_domain(article_url, self._domain):
            raise ValueError(f"Invalid URL: {article_url}. Must belong to domain {self._domain}")
        
        if not VinewsValidator.validate_html_url(article_url):
            raise ValueError(f"Invalid URL: {article_url}. An Article must be an HTML page.")

        article_html = self.fetch(article_url)
        
        return self._article_parser.parse_article(
            url=article_url, 
            response=article_html
        )
    
    def scrape_homepage(self) -> Homepage:
        """
        Scrapes the homepage of VnExpress and returns a structured Homepage object.

        :return: A Homepage object containing the parsed data.
        :rtype: Homepage
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the homepage is missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the homepage contains unexpected elements.
        """
        homepage_html = self.fetch(self._base_url)
        
        return self._page_parser.parse_homepage(homepage_html)
    
    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=2, max=10),
        stop=tenacity.stop_after_attempt(5),
        reraise=True,
        retry=tenacity.retry_if_exception_type(httpx.HTTPStatusError)
    )
    async def async_fetch(self, url: str) -> str:
        """
        Asynchronously fetches a VnExpress page from the given URL.

        :param url: The URL of the page to fetch.
        :type url: str
        :return: A string containing the HTML content of the page.
        :rtype: str
        :raises ValueError: If the provided URL does not belong to the domain (vnexpress.net).
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        """
        if not VinewsValidator.validate_url_with_domain(url, self._domain):
            raise ValueError(f"Invalid URL: {url}. Must belong to domain {self._domain}")

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(url, headers=self._headers)
            response.raise_for_status()

        return response.text
    
    async def async_scrape_article(self, article_url: str) -> Article:
        """
        Asynchronously scrapes an article from the given URL.

        :param article_url: The URL of the article to scrape.
        :type article_url: str
        :return: An Article object containing the parsed article data.
        :rtype: Article
        :raises ValueError: If the provided URL does not belong to the domain or is not an HTML page.
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the article is missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the article contains unexpected elements.
        """
        if not VinewsValidator.validate_url_with_domain(article_url, self._domain):
            raise ValueError(f"Invalid URL: {article_url}. Must belong to domain {self._domain}")
        
        if not VinewsValidator.validate_html_url(article_url):
            raise ValueError(f"Invalid URL: {article_url}. An Article must be an HTML page.")

        article_html = await self.async_fetch(article_url)

        return self._article_parser.parse_article(
            url=article_url, 
            response=article_html
        )
    
    async def async_scrape_homepage(self) -> Homepage:
        """
        Asynchronously scrapes the homepage of VnExpress and returns a structured Homepage object.

        :return: A Homepage object containing the parsed data.
        :rtype: Homepage
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the homepage is missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the homepage contains unexpected elements.
        """
        hompage_html = await self.async_fetch(self._base_url)

        return self._page_parser.parse_homepage(hompage_html)
    