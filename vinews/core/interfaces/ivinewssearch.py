from typing import Protocol, Optional, Union, Literal
from vinews.core.models import SearchResults, SearchResultsArticles, Homepage

class IVinewsSearch(Protocol):
    """
    Interface for a search functionality that allows searching for news articles
    """

    def search(
        self,
        query: str,
        date_range: Optional[Literal["day", "week", "month", "year"]] = None,
        category: Optional[str] = None,
        advanced: bool = False,
        limit: int = 5
    ) -> Union[SearchResults, SearchResultsArticles]:
        """
        Searches for news articles on VnExpress based on the provided query, date range, and category.

        :param str query: The search query string.
        :param Optional[Literal["day", "week", "month", "year"]] date_range: Optional date range filter for the search results.
        :param Optional[VnExpressSearchCategory] category: Optional category filter for the search results.
        :param bool advanced: If True, returns SearchResultsArticles instead of SearchResults. Note that this will only fetch the first 5 articles to avoid performance issues and rate limits.
        :param limit: Optional limit for the number of articles to fetch, defaults to 5 if not specified. Only support range from 1 to 5.
        :return: A SearchResults or SearchResultsArticles object containing the search results.
        :rtype: Union[SearchResults, SearchResultsArticles]
        :raises ValueError: If the limit is not between 1 and 5.
        :raises vinews.core.exceptions.MissingElementError: If the search results are missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the search results contain unexpected elements.
        """
        ...

    def fetch_homepage(self) -> Homepage:
        """
        Fetches the homepage and returns a structured Homepage object.

        :return: A Homepage object containing the parsed data.
        :rtype: Homepage
        :raises vinews.core.exceptions.MissingElementError: If the homepage is missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the homepage contains unexpected elements.
        """
        ...

class AsyncIVinewsSearch(Protocol):
    """
    Asynchronous interface for a search functionality that allows searching for news articles
    """

    async def async_search(
        self,
        query: str,
        date_range: Optional[Literal["day", "week", "month", "year"]] = None,
        category: Optional[str] = None,
        advanced: bool = False
    ) -> Union[SearchResults, SearchResultsArticles]:
        """
        Asynchronously searches for news articles based on the provided query, date range, and category.
        
        :param str query: The search query string.
        :param Optional[Literal["day", "week", "month", "year"]] date_range: Optional date range filter for the search results.
        :param Optional[str] category: Optional category filter for the search results.
        :param bool advanced: If True, returns SearchResultsArticles instead of SearchResults.
        :return: A SearchResults or SearchResultsArticles object containing the search results.
        :rtype: Union[SearchResults, SearchResultsArticles]
        :raises vinews.core.exceptions.MissingElementError: If the search results are missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the search results contain unexpected elements.
        """
        ...

    async def async_fetch_homepage(self) -> Homepage:
        """
        Asynchronously fetches the homepage and returns a structured Homepage object.

        :return: A Homepage object containing the parsed data.
        :rtype: Homepage
        :raises vinews.core.exceptions.MissingElementError: If the homepage is missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the homepage contains unexpected elements.
        """
        ...