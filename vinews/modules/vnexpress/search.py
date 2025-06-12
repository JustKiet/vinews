from vinews.core.models import (
    SearchResults, SearchResultsArticles, Article, 
    HomepageArticles, CategorizedNewsArticles, TopNewsArticles,
)
from vinews.modules.vnexpress.scrapers import VinewsVnExpressScraper
from vinews.modules.vnexpress.parsers import VinewsVnExpressPageParser
from vinews.core.exceptions import MissingElementError
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Literal, Union, Any, overload
from urllib.parse import urlencode
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

VnExpressSearchCategory = Literal[
    "kinhdoanh", "cong-dong", "phap-luat", "the-gioi", "dulich",
    "khoa-hoc-cong-nghe", "thoi-su", "oto-xe-may", "thethao",
    "doisong", "suckhoe"
]

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
        self._scraper = VinewsVnExpressScraper()
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

    def _safe_scrape_article(self, url: str) -> Optional[Article]:
        """
        Safely scrapes an article from the provided URL.

        :param url: The URL of the article to scrape.
        :return: An Article object if successful, None if an error occurs.
        :rtype: Optional[Article]
        """
        try:
            return self._scraper.scrape_article(url)
        except Exception as e:
            logger.warning(f"Failed to scrape article at url: '{url}'. Error: {e}")
            return None

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
        limit: int = 5,
    ) -> SearchResultsArticles: 
        """
        Searches for news articles on VnExpress based on the provided query, date range, and category.
        
        :param str query: The search query string.
        :param Optional[Literal["day", "week", "month", "year"]] date_range: Optional date range filter for the search results.
        :param Optional[VnExpressSearchCategory] category: Optional category filter for the search results.
        :param Literal[True] advanced: Must be `True`, returns SearchResultsArticles instead of SearchResults.
        :param limit: Optional limit for the number of articles to fetch, defaults to 5 if not specified. Only support range from 1 to 5.
        :return: An SearchResultsArticles object containing the search results with detailed articles.
        :rtype: SearchResultsArticles
        :raises ValueError: If the limit is not between 1 and 5.
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the search results are missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the search results contain unexpected elements.
        """
        ...

    def search(
        self, 
        query: str, 
        date_range: Optional[Literal["day", "week", "month", "year"]] = None,
        category: Optional[VnExpressSearchCategory] = None,
        advanced: bool = False,
        limit: int = 5,
    ) -> Union[SearchResults, SearchResultsArticles]:
        """
        Searches for news articles on VnExpress based on the provided query, date range, and category.

        :param str query: The search query string.
        :param Optional[Literal["day", "week", "month", "year"]] date_range: Optional date range filter for the search results.
        :param Optional[VnExpressSearchCategory] category: Optional category filter for the search results.
        :param bool advanced: If True, returns SearchResultsArticles instead of SearchResults. Note that this will only fetch the first 5 articles to avoid performance issues and rate limits.
        :param limit: Optional limit for the number of articles to fetch, defaults to 5 if not specified. Only support range from 1 to 10.
        :return: A SearchResults or SearchResultsArticles object containing the search results.
        :rtype: Union[SearchResults, SearchResultsArticles]
        :raises ValueError: If the limit is not between 1 and 10.
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the search results are missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the search results contain unexpected elements.
        """
        if limit < 1 or limit > 10:
            raise ValueError("Limit must be between 1 and 10.")
        
        params = {"q": query, "media_type": "text"}

        if date_range:
            params["date_format"] = date_range

        if category:
            params["cate_code"] = category

        query_string = urlencode(params)

        search_url = f"{self._base_search_url}?{query_string}"

        search_results_html = self._scraper.fetch(search_url)

        try:
            news_cards = self._page_parser.parse_search_results(response=search_results_html)
        except MissingElementError:
            logger.error("Search results are missing expected elements. Perhaps the search query returned no results or the structure of the page has changed.")
            return SearchResults(
                url=search_url,
                domain=self._domain,
                params=params,
                results=[],
                total_results=0,
                timestamp=int(datetime.now().timestamp())
            )

        articles: list[Article] = []

        if advanced:
            urls = [card.url for card in news_cards]

            with ThreadPoolExecutor(max_workers=self._semaphore_limit) as executor:
                results = list(executor.map(self._safe_scrape_article, urls[:limit]))

            articles = [result for result in results if isinstance(result, Article)]
                
            return SearchResultsArticles(
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
        limit: int = 5,
    ) -> SearchResultsArticles: 
        """
        Searches for news articles on VnExpress based on the provided query, date range, and category.
        
        :param str query: The search query string.
        :param Optional[Literal["day", "week", "month", "year"]] date_range: Optional date range filter for the search results.
        :param Optional[VnExpressSearchCategory] category: Optional category filter for the search results.
        :param Literal[True] advanced: Must be `True`, returns SearchResultsArticles instead of SearchResults. 
        Note that this will only fetch the first 5 articles for performance and avoiding rate limits.
        :param limit: Optional limit for the number of articles to fetch, defaults to 5 if not specified. Only support range from 1 to 5.
        :return: An SearchResultsArticles object containing the search results with detailed articles.
        :rtype: SearchResultsArticles
        :raises ValueError: If the limit is not between 1 and 5.
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
        limit: int = 5,
    ) -> Union[SearchResults, SearchResultsArticles]:
        """
        Asynchronously searches for news articles on VnExpress based on the provided query, date range, and category.

        :param str query: The search query string.
        :param Optional[Literal["day", "week", "month", "year"]] date_range: Optional date range filter for the search results.
        :param Optional[VnExpressSearchCategory] category: Optional category filter for the search results.
        :param bool advanced: If True, returns SearchResultsArticles instead of SearchResults.
        Note that this will only fetch the first 5 articles for performance and avoiding rate limits.
        :param limit: Optional limit for the number of articles to fetch, defaults to 5 if not specified. Only support range from 1 to 10.
        :return: A SearchResults or SearchResultsArticles object containing the search results.
        :rtype: Union[SearchResults, SearchResultsArticles]
        :raises ValueError: If the limit is not between 1 and 10.
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the search results are missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the search results contain unexpected elements.
        """
        if limit < 1 or limit > 10:
            raise ValueError("Limit must be between 1 and 10.")
        
        params = {"q": query}

        if date_range:
            params["date_format"] = date_range

        if category:
            params["cate_code"] = category

        query_string = urlencode(params)

        search_url = f"{self._base_search_url}?{query_string}"

        search_results_html = await self._scraper.async_fetch(search_url)

        try:
            news_cards = self._page_parser.parse_search_results(response=search_results_html)
        except MissingElementError:
            logger.error("Search results are missing expected elements. Perhaps the search query returned no results or the structure of the page has changed.")
            return SearchResults(
                url=search_url,
                domain=self._domain,
                params=params,
                results=[],
                total_results=0,
                timestamp=int(datetime.now().timestamp())
            )

        articles: list[Union[Article, BaseException]] = []

        if advanced:
            urls = [card.url for card in news_cards]

            tasks = [self._scraper.async_scrape_article(url) for url in urls[:limit]]

            articles = await asyncio.gather(*tasks, return_exceptions=True)

            articles_filtered = [article for article in articles if isinstance(article, Article)]

            return SearchResultsArticles(
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
    
    def search_homepage(self) -> HomepageArticles:
        """
        Searches the homepage of VnExpress and returns a structured HomepageArticles object.

        :return: A HomepageArticles object containing the parsed data with scraped articles.
        :rtype: HomepageArticles
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the homepage is missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the homepage contains unexpected elements.
        """
        homepage_news_cards = self._scraper.scrape_homepage()

        latest_news_url = [card.url for card in homepage_news_cards.latest_news]

        latest_news_articles: list[Article] = []
        
        for url in latest_news_url:
            try:
                latest_news_articles.append(self._scraper.scrape_article(url))
            except Exception as e:
                logger.warning(f"Failed to scrape article at url: '{url}'. Error: {e}")
                continue

        categorized_news_articles: list[CategorizedNewsArticles] = []

        for categorized_news in homepage_news_cards.categorized_news:
            if not categorized_news.news_cards:
                logger.warning(f"Skipping categorized news '{categorized_news.category}' as it has no articles.")
                continue

            urls = [article.url for article in categorized_news.news_cards]

            # Use ThreadPoolExecutor to scrape articles concurrently
            with ThreadPoolExecutor(max_workers=self._semaphore_limit) as executor:
                results = list(executor.map(self._safe_scrape_article, urls))

            # Filter out None results (failed scrapes)
            cat_articles = [result for result in results if isinstance(result, Article)]

            categorized_news_articles.append(
                CategorizedNewsArticles(
                    category=categorized_news.category,
                    articles=cat_articles,
                    total_articles=len(categorized_news.news_cards)
                )
            )

        all_top_articles: list[Article] = []

        try:
            all_top_articles.append(
                self._scraper.scrape_article(homepage_news_cards.top_news.featured.url)
            )
        except Exception as e:
            logger.warning(f"Failed to scrape featured top news article at url: '{homepage_news_cards.top_news.featured.url}'. Error: {e}")
            pass

        sub_featured_urls = [article.url for article in homepage_news_cards.top_news.sub_featured]

        # Use ThreadPoolExecutor to scrape sub-featured top news articles concurrently
        with ThreadPoolExecutor(max_workers=self._semaphore_limit) as executor:
            results = list(executor.map(self._safe_scrape_article, sub_featured_urls))

        # Filter out None results (failed scrapes)
        all_top_articles.extend(
            [result for result in results if isinstance(result, Article)]
        )

        # If the featured article failed to scrape, we should not include it in the top news articles
        if not all_top_articles:
            logger.warning("No top news articles could be scraped. Skipping top news section.")
            all_top_articles = []

            top_news_articles = TopNewsArticles(
                featured=None,
                sub_featured=[],
                total_articles=0
            )
        elif len(all_top_articles) < 2:
            logger.warning("Not enough top news articles scraped. At least 2 articles are required for top news section.")
            top_news_articles = TopNewsArticles(
                featured=all_top_articles[0],
                sub_featured=[],
                total_articles=len(all_top_articles)
            )
        else:
            top_news_articles = TopNewsArticles(
                featured=all_top_articles[0],
                sub_featured=all_top_articles[1:],
                total_articles=len(all_top_articles)
            )

        return HomepageArticles(
            url=self._homepage_url,
            domain=self._domain,
            top_news=top_news_articles,
            latest_news=latest_news_articles,
            categorized_news=categorized_news_articles,
            total_articles=len(latest_news_articles) + len(categorized_news_articles),
            timestamp=int(datetime.now().timestamp())
        )
    
    async def async_search_homepage(self) -> HomepageArticles:
        """
        Asynchronously searches the homepage of VnExpress and returns a structured HomepageArticles object.

        :return: A HomepageArticles object containing the parsed data and scraped articles.
        :rtype: HomepageArticles
        :raises httpx.HTTPStatusError: If the HTTP request fails with a non-2xx status code.
        :raises vinews.core.exceptions.MissingElementError: If the homepage is missing expected elements.
        :raises vinews.core.exceptions.UnexpectedElementError: If the homepage contains unexpected elements.
        """
        homepage_news_cards = await self._scraper.async_scrape_homepage()

        latest_news_url = [card.url for card in homepage_news_cards.latest_news]

        tasks = [self._scraper.async_scrape_article(url) for url in latest_news_url]

        results = await asyncio.gather(*tasks, return_exceptions=True)
    
        latest_news_articles = [result for result in results if isinstance(result, Article)]

        categorized_news_articles: list[CategorizedNewsArticles] = []

        for categorized_news in homepage_news_cards.categorized_news:
            if not categorized_news.news_cards:
                logger.warning(f"Skipping categorized news '{categorized_news.category}' as it has no articles.")
                continue

            cat_articles: list[Article] = []

            tasks = [
                self._scraper.async_scrape_article(article.url) 
                for article in categorized_news.news_cards
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            cat_articles.extend(
                [result for result in results if isinstance(result, Article)]
            )

            categorized_news_articles.append(
                CategorizedNewsArticles(
                    category=categorized_news.category,
                    articles=cat_articles,
                    total_articles=len(cat_articles)
                )
            )

        all_articles: list[Article] = []

        try:
            all_articles.append(
                await self._scraper.async_scrape_article(homepage_news_cards.top_news.featured.url)
            )
        except Exception as e:
            logger.warning(f"Failed to scrape featured top news article at url: '{homepage_news_cards.top_news.featured.url}'. Error: {e}")
            pass

        tasks = [
            self._scraper.async_scrape_article(article.url) 
            for article in homepage_news_cards.top_news.sub_featured
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_articles.extend(
            [result for result in results if isinstance(result, Article)]
        )

        if not all_articles:
            logger.warning("No top news articles could be scraped. Skipping top news section.")
            all_articles = []

            top_news_articles = TopNewsArticles(
                featured=None,
                sub_featured=[],
                total_articles=0
            )
        elif len(all_articles) < 2:
            logger.warning("Not enough top news articles scraped. At least 2 articles are required for top news section.")
            top_news_articles = TopNewsArticles(
                featured=all_articles[0],
                sub_featured=[],
                total_articles=len(all_articles)
            )
        else:
            top_news_articles = TopNewsArticles(
                featured=all_articles[0],
                sub_featured=all_articles[1:],
                total_articles=len(all_articles)
            )

        return HomepageArticles(
            url=self._homepage_url,
            domain=self._domain,
            top_news=top_news_articles,
            latest_news=latest_news_articles,
            categorized_news=categorized_news_articles,
            total_articles=len(latest_news_articles) + len(categorized_news_articles),
            timestamp=int(datetime.now().timestamp())
        )
