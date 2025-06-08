from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta
from bs4 import Tag
from typing import Any
from vinews.core.exceptions import MissingElementError, UnexpectedElementError
import re

class VinewsValidator:
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validates if the given URL is well-formed.

        :param url: The URL to validate.
        :return: True if the URL is well-formed, False otherwise.
        """
        try:
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc])
        except Exception:
            return False

    @staticmethod
    def validate_url_with_domain(url: str, domain: str) -> bool:
        """
        Validates if the given URL belongs to the specified domain.

        :param url: The URL to validate.
        :param domain: The domain to check against.
        :return: True if the URL belongs to the domain, False otherwise.
        """
        try:
            parsed = urlparse(url)
            if parsed.scheme in ("http", "https") and parsed.hostname and parsed.hostname.endswith(domain):
                return True
            else:
                return False
        except Exception:
            return False

    @staticmethod
    def parse_vi_datetime_string(date_str: str) -> datetime:
        """
        Parses a Vietnamese date string that contains dd/mm/yyyy, HH:mm, and assumes the timezone is GMT+7 (Vietnam).
        anywhere inside, ignoring other parts (e.g. weekday in Vietnamese).

        :param date_str: Input string
        :return: timezone-aware datetime.datetime object
        :raises ValueError: if pattern not found or parsing fails
        """
        # Regex to find dd/mm/yyyy and HH:mm ignoring any extra text
        pattern = r"(\d{1,2}/\d{1,2}/\d{4}),?\s*(\d{2}:\d{2})"

        match = re.search(pattern, date_str)
        if not match:
            raise ValueError("Input string does not contain expected date and time.")

        date_only, time_only = match.groups()

        dt = datetime.strptime(f"{date_only} {time_only}", "%d/%m/%Y %H:%M")

        # Fixed GMT+7 timezone
        tzinfo = timezone(timedelta(hours=7))

        return dt.replace(tzinfo=tzinfo)

    @staticmethod
    def validate_tag(element: Any) -> Tag:
        """
        Validates if the provided element is a BeautifulSoup Tag.

        :param Any element: The element to be validated.
        :return: True if the element is a Tag, False otherwise.
        :rtype: Tag
        :raises MissingElementError: If the element is None or not found in the HTML document.
        :raises UnexpectedElementError: If the element is not a BeautifulSoup Tag.
        """
        if not element:
            raise MissingElementError("Element not found in the HTML document")
        
        if not isinstance(element, Tag):
            raise UnexpectedElementError(f"Expected a BeautifulSoup Tag, got {type(element)}")
        
        return element
    
    @staticmethod
    def validate_tags(elements: list[Any]) -> list[Tag]:
        """
        Validates if the provided elements are all BeautifulSoup Tags.

        :param list[Any] elements: The list of elements to be validated.
        :return: A list of validated BeautifulSoup Tags.
        :rtype: list[Tag]
        :raises MissingElementError: If no elements are found in the HTML document.
        :raises UnexpectedElementError: If any element is not a BeautifulSoup Tag.
        """
        if not elements:
            raise MissingElementError("No elements found in the HTML document")
        
        validated_tags: list[Tag] = []
        for element in elements:
            validated_tags.append(VinewsValidator.validate_tag(element))
        
        return validated_tags