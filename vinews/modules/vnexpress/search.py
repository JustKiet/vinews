from vinews.core.models import SearchResults, Homepage, AdvancedSearchResults
from vinews.modules.vnexpress.parsers import VinewsVnExpressPageParser
from vinews.modules.vnexpress.enums import VnExpressSearchCategory

from typing import Optional, Literal, Union, overload
from urllib.parse import urlencode
from datetime import datetime
import httpx

class VinewsVnExpressSearch:
    def __init__(self) -> None:
        self._homepage_url = "https://vnexpress.net/"
        self._domain = "vnexpress.net"
        self._base_search_url = "https://timkiem.vnexpress.net/"
        self._page_parser = VinewsVnExpressPageParser()

    @overload
    def search(
        self,
        *,
        query: str,
        date_range: Optional[Literal["day", "week", "month", "year"]] = None,
        category: Optional[VnExpressSearchCategory] = None,
        advanced: Literal[True]
    ) -> AdvancedSearchResults: ...

    @overload
    def search(
        self,
        *,
        query: str,
        date_range: Optional[Literal["day", "week", "month", "year"]] = None,
        category: Optional[VnExpressSearchCategory] = None,
        advanced: Literal[False]
    ) -> SearchResults: ...

    def search(
        self, 
        query: str, 
        date_range: Optional[Literal["day", "week", "month", "year"]] = None,
        category: Optional[VnExpressSearchCategory] = None,
        advanced: bool = False
    ) -> Union[SearchResults, AdvancedSearchResults]:
        """
        Searches for news articles on VnExpress based on the provided query, date range, and category.

        :param str query: The search query string.
        :param Optional[Literal["day", "week", "month", "year"]] date_range: Optional date range filter for the search results.
        :param Optional[VnExpressSearchCategory] category: Optional category filter for the search results.
        :param bool advanced: If True, returns AdvancedSearchResults instead of SearchResults.
        :return: A SearchResults or AdvancedSearchResults object containing the search results.
        :rtype: Union[SearchResults, AdvancedSearchResults]
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the search results are missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the search results contain unexpected elements.
        """
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

        # TODO: Implement advanced search results parsing
        # ...

        return SearchResults(
            url=search_url,
            domain=self._domain,
            results=news_cards,
            total_results=len(news_cards),
            timestamp=int(datetime.now().timestamp())
        )
            
    async def async_search(
        self, 
        query: str, 
        date_range: Optional[Literal["day", "week", "month", "year"]] = None,
        category: Optional[VnExpressSearchCategory] = None
    ) -> SearchResults:
        """
        Asynchronously searches for news articles on VnExpress based on the provided query, date range, and category.

        :param str query: The search query string.
        :param Optional[Literal["day", "week", "month", "year"]] date_range: Optional date range filter for the search results.
        :param Optional[VnExpressSearchCategory] category: Optional category filter for the search results.
        :return: A SearchResults object containing the search results.
        :rtype: SearchResults
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the search results are missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the search results contain unexpected elements.
        """
        params = {"q": query}

        if date_range:
            params["date_range"] = date_range

        if category:
            params["category"] = category.value

        query_string = urlencode(params)
        search_url = f"{self._base_search_url}?{query_string}"

        async with httpx.AsyncClient() as client:
            response = await client.get(search_url)
            response.raise_for_status()

        news_cards = self._page_parser.parse_search_results(response=response.text)

        return SearchResults(
            url=search_url,
            domain=self._domain,
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
