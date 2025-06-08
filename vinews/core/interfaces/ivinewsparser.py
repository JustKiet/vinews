from vinews.core.models import (
    Article, NewsCard,
    Homepage, TopicPage
)
from typing import Protocol

class IVinewsArticleParser(Protocol):
    """
    Interface for a parser that processes text input and returns a structured output.
    """

    def parse_article(self, url: str, response: str) -> Article:
        """
        Parses the given article at the given URL and returns a structured output.

        :param str url: The URL of the article for referencing in the Article object.
        :param str response: The HTML response content of the article.
        :return: An Article object containing the parsed data.
        :rtype: Article
        :raises InvalidURLError: If the provided URL is not a valid VnExpress article URL.
        :raises MissingElementError: If the article section or required elements are not found.
        :raises UnexpectedElementError: If an unexpected element type is encountered.
        """
        ...

class IVinewsPageParser(Protocol):
    """
    Interface for a parser that processes text input and returns a structured output.
    """

    def parse_homepage(self, response: str) -> Homepage:
        """
        Parses the homepage and returns a structured Homepage object.

        :param str response: The HTML response content of the homepage.
        :return: A Homepage object containing the parsed data.
        :rtype: Homepage
        :raises MissingElementError: If the homepage is missing expected elements.
        :raises UnexpectedElementError: If the homepage contains unexpected elements.
        """
        ...

    def parse_topic(self, response: str) -> TopicPage:
        """
        Parses the given topic page and returns a structured TopicPage object.

        :param str response: The HTML response content of the topic page.
        :return: A TopicPage object containing the parsed data.
        :rtype: TopicPage
        :raises MissingElementError: If the topic section or required elements are not found.
        :raises UnexpectedElementError: If an unexpected element type is encountered.
        """
        ...

    def parse_search_results(self, response: str) -> list[NewsCard]:
        """
        Parses the search results page and returns a list of NewsCard objects.

        :param str response: The HTML response content of the search results page.
        :return: A list of NewsCard objects representing the search results.
        :rtype: list[NewsCard]
        :raises MissingElementError: If the search results section or required elements are not found.
        :raises UnexpectedElementError: If an unexpected element type is encountered.
        """
        ...