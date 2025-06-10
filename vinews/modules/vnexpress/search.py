from vinews.core.models import SearchResults, Homepage, AdvancedSearchResults, Article
from vinews.modules.vnexpress.parsers import VinewsVnExpressPageParser, VinewsVnExpressArticleParser
from vinews.modules.vnexpress.enums import VnExpressSearchCategory

from typing import Optional, Literal, Union, Any, overload
from urllib.parse import urlencode
from datetime import datetime
import httpx
import asyncio

class VinewsVnExpressSearch:
    def __init__(self, timeout: int = 10, **kwargs: Any) -> None:
        if timeout <= 0:
            raise ValueError("Timeout must be a positive integer.")
        self._timeout = timeout

        if "semaphore_limit" in kwargs and (not isinstance(kwargs["semaphore_limit"], int) or kwargs["semaphore_limit"] <= 0):
            raise ValueError("semaphore_limit must be a positive integer.")
        
        self._semaphore_limit = kwargs.get("semaphore_limit", 5)
        self._homepage_url = "https://vnexpress.net/"
        self._domain = "vnexpress.net"
        self._base_search_url = "https://timkiem.vnexpress.net/"
        self._article_parser = VinewsVnExpressArticleParser()
        self._page_parser = VinewsVnExpressPageParser()
        self._semaphore = asyncio.Semaphore(self._semaphore_limit)

    @property
    def timeout(self) -> int:
        """
        Returns the timeout value in seconds.
        """
        return self._timeout
    
    @timeout.setter
    def timeout(self, value: int) -> None:
        """
        Sets the timeout value in seconds.

        :param value: The timeout value in seconds, must be a positive integer.
        :raises ValueError: If the provided value is not a positive integer.
        """
        if value <= 0:
            raise ValueError("Timeout must be a positive integer.")
        self._timeout = value

    @overload
    def search(
        self,
        *,
        query: str,
        date_range: Optional[Literal["day", "week", "month", "year"]] = None,
        category: Optional[VnExpressSearchCategory] = None,
    ) -> SearchResults: 
        """
        Searches for news articles on VnExpress based on the provided query, date range, and category.
        :param str query: The search query string.
        :param Optional[Literal["day", "week", "month", "year"]] date_range: Optional date range filter for the search results.
        :param Optional[VnExpressSearchCategory] category: Optional category filter for the search results.
        :return: A SearchResults object containing the search results.
        :rtype: SearchResults
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the search results are missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the search results contain unexpected elements.
        """
        ...

    @overload
    def search(
        self,
        *,
        query: str,
        date_range: Optional[Literal["day", "week", "month", "year"]] = None,
        category: Optional[VnExpressSearchCategory] = None,
        advanced: Literal[True],
        **kwargs: Any,
    ) -> AdvancedSearchResults: 
        """
        Searches for news articles on VnExpress based on the provided query, date range, and category.
        
        :param str query: The search query string.
        :param Optional[Literal["day", "week", "month", "year"]] date_range: Optional date range filter for the search results.
        :param Optional[VnExpressSearchCategory] category: Optional category filter for the search results.
        :param Literal[True] advanced: Must be `True`, returns AdvancedSearchResults instead of SearchResults.
        :param kwargs: Additional keyword arguments, such as limit for the number of articles to fetch.
        :return: An AdvancedSearchResults object containing the search results with detailed articles.
        :rtype: AdvancedSearchResults
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the search results are missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the search results contain unexpected elements.
        :raises TypeError: If the `advanced` parameter is not True when additional keyword arguments are provided.
        """
        ...

    def search(
        self, 
        query: str, 
        date_range: Optional[Literal["day", "week", "month", "year"]] = None,
        category: Optional[VnExpressSearchCategory] = None,
        advanced: bool = False,
        **kwargs: Any,
    ) -> Union[SearchResults, AdvancedSearchResults]:
        """
        Searches for news articles on VnExpress based on the provided query, date range, and category.

        :param str query: The search query string.
        :param Optional[Literal["day", "week", "month", "year"]] date_range: Optional date range filter for the search results.
        :param Optional[VnExpressSearchCategory] category: Optional category filter for the search results.
        :param bool advanced: If True, returns AdvancedSearchResults instead of SearchResults. Note that this will only fetch the first 5 articles to 
        :return: A SearchResults or AdvancedSearchResults object containing the search results.
        :rtype: Union[SearchResults, AdvancedSearchResults]
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the search results are missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the search results contain unexpected elements.
        """
        limit = kwargs.get("limit", 5)  # Default limit to 5 articles if not specified
        params = {"q": query}

        if date_range:
            params["date_range"] = date_range

        if category:
            params["category"] = category.value

        query_string = urlencode(params)
        search_url = f"{self._base_search_url}?{query_string}"

        with httpx.Client() as client:
            response = client.get(search_url)
            response.raise_for_status()

        news_cards = self._page_parser.parse_search_results(response=response.text)

        articles: list[Article] = []

        if advanced:
            urls = [card.url for card in news_cards]

            for url in urls[:limit]: # Limit to first 10 articles for performance and avoiding rate limits
                with httpx.Client(timeout=self._timeout) as client:
                    response = client.get(url)
                    response.raise_for_status()
                
                try:
                    articles.append(self._article_parser.parse_article(url, response=response.text))
                except Exception as e:
                    continue  # Skip articles that cannot be parsed
                
            return AdvancedSearchResults(
                url=search_url,
                domain=self._domain,
                params=params,
                results=articles,
                total_results=len(articles),
                timestamp=int(datetime.now().timestamp())
            )
                
        return SearchResults(
            url=search_url,
            domain=self._domain,
            params=params,
            results=news_cards,
            total_results=len(news_cards),
            timestamp=int(datetime.now().timestamp())
        )
    
    async def _async_fetch_and_parse(self, url: str) -> Optional[Article]:
        async with self._semaphore:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
            try:
                return self._article_parser.parse_article(url, response=response.text)
            except Exception as e:
                pass
    
    @overload
    async def async_search(
        self,
        *,
        query: str,
        date_range: Optional[Literal["day", "week", "month", "year"]] = None,
        category: Optional[VnExpressSearchCategory] = None,
    ) -> SearchResults: 
        """
        Searches for news articles on VnExpress based on the provided query, date range, and category.
        :param str query: The search query string.
        :param Optional[Literal["day", "week", "month", "year"]] date_range: Optional date range filter for the search results.
        :param Optional[VnExpressSearchCategory] category: Optional category filter for the search results.
        :return: A SearchResults object containing the search results.
        :rtype: SearchResults
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the search results are missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the search results contain unexpected elements.
        """
        ...

    @overload
    async def async_search(
        self,
        *,
        query: str,
        date_range: Optional[Literal["day", "week", "month", "year"]] = None,
        category: Optional[VnExpressSearchCategory] = None,
        advanced: Literal[True],
        **kwargs: Any,
    ) -> AdvancedSearchResults: 
        """
        Searches for news articles on VnExpress based on the provided query, date range, and category.
        
        :param str query: The search query string.
        :param Optional[Literal["day", "week", "month", "year"]] date_range: Optional date range filter for the search results.
        :param Optional[VnExpressSearchCategory] category: Optional category filter for the search results.
        :param Literal[True] advanced: Must be `True`, returns AdvancedSearchResults instead of SearchResults. 
        Note that this will only fetch the first 5 articles (can be tweaked by setting `limit` in **kwargs, use with caution) for performance and avoiding rate limits.
        :param kwargs: Additional keyword arguments, such as limit for the number of articles to fetch.
        :return: An AdvancedSearchResults object containing the search results with detailed articles.
        :rtype: AdvancedSearchResults
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the search results are missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the search results contain unexpected elements.
        :raises TypeError: If the `advanced` parameter is not True when additional keyword arguments are provided.
        """
        ...
            
    async def async_search(
        self, 
        query: str, 
        date_range: Optional[Literal["day", "week", "month", "year"]] = None,
        category: Optional[VnExpressSearchCategory] = None,
        advanced: bool = False,
        **kwargs: Any,
    ) -> Union[SearchResults, AdvancedSearchResults]:
        """
        Asynchronously searches for news articles on VnExpress based on the provided query, date range, and category.

        :param str query: The search query string.
        :param Optional[Literal["day", "week", "month", "year"]] date_range: Optional date range filter for the search results.
        :param Optional[VnExpressSearchCategory] category: Optional category filter for the search results.
        :param bool advanced: If True, returns AdvancedSearchResults instead of SearchResults.
        Note that this will only fetch the first 5 articles (can be tweaked by setting `limit` in **kwargs, use with caution) for performance and avoiding rate limits.
        :return: A SearchResults or AdvancedSearchResults object containing the search results.
        :rtype: Union[SearchResults, AdvancedSearchResults]
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the search results are missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the search results contain unexpected elements.
        """
        limit = kwargs.get("limit", 5)  # Default limit to 5 articles if not specified
        params = {"q": query}

        if date_range:
            params["date_range"] = date_range

        if category:
            params["category"] = category.value

        query_string = urlencode(params)
        search_url = f"{self._base_search_url}?{query_string}"

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(search_url)
            response.raise_for_status()

        news_cards = self._page_parser.parse_search_results(response=response.text)

        articles: list[Optional[Article]] = []

        if advanced:
            urls = [card.url for card in news_cards]

            tasks = [self._async_fetch_and_parse(url) for url in urls[:limit]]
            articles = await asyncio.gather(*tasks)

            articles_filtered = [article for article in articles if article is not None]  # Filter out None values

            return AdvancedSearchResults(
                url=search_url,
                domain=self._domain,
                params=params,
                results=articles_filtered,
                total_results=len(articles),
                timestamp=int(datetime.now().timestamp())
            )

        return SearchResults(
            url=search_url,
            domain=self._domain,
            params=params,
            results=news_cards,
            total_results=len(news_cards),
            timestamp=int(datetime.now().timestamp())
        )
    
    def fetch_homepage(self) -> Homepage:
        """
        Fetches the homepage of VnExpress and returns a structured Homepage object.

        :return: A Homepage object containing the parsed data.
        :rtype: Homepage
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the homepage is missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the homepage contains unexpected elements.
        """
        with httpx.Client() as client:
            response = client.get(self._homepage_url)
            response.raise_for_status()

        return self._page_parser.parse_homepage(response=response.text)
    
    async def async_fetch_homepage(self) -> Homepage:
        """
        Asynchronously fetches the homepage of VnExpress and returns a structured Homepage object.

        :return: A Homepage object containing the parsed data.
        :rtype: Homepage
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the homepage is missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the homepage contains unexpected elements.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(self._homepage_url)
            response.raise_for_status()

        return self._page_parser.parse_homepage(response=response.text)
