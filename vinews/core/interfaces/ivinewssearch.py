from typing import Protocol, Optional, Union, Literal
from vinews.core.models import SearchResults, AdvancedSearchResults, Homepage

class IVinewsSearch(Protocol):
    """
    Interface for a search functionality that allows searching for news articles
    """

    def search(
        self,
        query: str,
        date_range: Optional[Literal["day", "week", "month", "year"]] = None,
        category: Optional[str] = None,
        advanced: bool = False
    ) -> Union[SearchResults, AdvancedSearchResults]:
        """
        Searches for news articles based on the provided query, date range, and category.

        :param str query: The search query string.
        :param Optional[Literal["day", "week", "month", "year"]] date_range: Optional date range filter for the search results.
        :param Optional[str] category: Optional category filter for the search results.
        :param bool advanced: If True, returns AdvancedSearchResults instead of SearchResults.
        :return: A SearchResults or AdvancedSearchResults object containing the search results.
        :rtype: Union[SearchResults, AdvancedSearchResults]
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

    async def search(
        self,
        query: str,
        date_range: Optional[Literal["day", "week", "month", "year"]] = None,
        category: Optional[str] = None,
        advanced: bool = False
    ) -> Union[SearchResults, AdvancedSearchResults]:
        """
        Asynchronously searches for news articles based on the provided query, date range, and category.
        
        :param str query: The search query string.
        :param Optional[Literal["day", "week", "month", "year"]] date_range: Optional date range filter for the search results.
        :param Optional[str] category: Optional category filter for the search results.
        :param bool advanced: If True, returns AdvancedSearchResults instead of SearchResults.
        :return: A SearchResults or AdvancedSearchResults object containing the search results.
        :rtype: Union[SearchResults, AdvancedSearchResults]
        :raises vinews.core.exceptions.MissingElementError: If the search results are missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the search results contain unexpected elements.
        """
        ...

    async def fetch_homepage(self) -> Homepage:
        """
        Asynchronously fetches the homepage and returns a structured Homepage object.

        :return: A Homepage object containing the parsed data.
        :rtype: Homepage
        :raises vinews.core.exceptions.MissingElementError: If the homepage is missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the homepage contains unexpected elements.
        """
        ...