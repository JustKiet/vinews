from vinews.core.interfaces.ivinewsparser import IVinewsArticleParser, IVinewsPageParser
from vinews.core.models import (
    Article, Media, NewsCard, Comment,
    TopNews, CategorizedNews, Homepage, TopicPage
)
from vinews.core.exceptions import (
    MissingElementError, UnexpectedElementError
)
from vinews.core.utils import VinewsValidator

from typing import Optional
from bs4 import BeautifulSoup
from bs4.element import Tag
from datetime import datetime
import markdownify # type: ignore
from urllib.parse import urljoin, urlparse
import re

class VinewsVnExpressArticleParser(IVinewsArticleParser):
    def __init__(self):
        self._domain = "vnexpress.net"

    def _parse_images(self, content_element: Tag, base_url: str) -> list[Media]:
        """
        Parses image elements from the content element and returns a list of Media objects. 

        :param Tag content_element: The content element containing image tags.
        :param str base_url: The base URL to resolve relative image URLs.
        :return: A list of Media objects representing the images.
        :rtype: list[Media]
        :raises MissingElementError: If no image elements are found or if an image element does not have 'data-src' or 'src' attribute.
        :raises UnexpectedElementError: If an image element's 'data-src' or 'src' attribute is not a string.
        """
        image_elements = VinewsValidator.validate_tags(
            elements=content_element.find_all('img')
        )

        media_list: list[Media] = []

        for img in image_elements:
            if not img.has_attr('data-src') and not img.has_attr('src'):
                raise MissingElementError("Image element does not have 'data-src' or 'src' attribute")

            data_src = img.get('data-src') or img.get('src')
            if not isinstance(data_src, str):
                raise UnexpectedElementError(f"Expected 'data-src' or 'src' attribute to be a string, got {type(data_src)}")
            
            url = urljoin(base_url, data_src)

            parsed_url = urlparse(url)
            format_ext = parsed_url.path.split('.')[-1].lower()

            description = img.get('alt')

            if not isinstance(description, (str, type(None))):
                raise UnexpectedElementError(f"Expected 'alt' attribute to be a string or None, got {type(description)}")

            media = Media(
                media_type='image',
                format=format_ext,
                src=data_src,
                description=description
            )
            media_list.append(media)

        return media_list
    
    def _parse_audio(self, content_element: Tag, base_url: str) -> list[Media]:
        """
        Parses audio elements from the content element and returns a list of Media objects.

        :param Tag content_element: The content element containing audio tags.
        :param str base_url: The base URL to resolve relative audio URLs.
        :return: A list of Media objects representing the audio files.
        :rtype: list[Media]
        :raises MissingElementError: If no audio elements are found or if an audio element does not have 'src' attribute.
        :raises UnexpectedElementError: If an audio element's 'src' attribute is not a string.
        """
        audio_elements = VinewsValidator.validate_tags(
            elements=content_element.find_all('audio')
        )

        media_list: list[Media] = []

        for audio in audio_elements:
            if not audio.has_attr('src'):
                raise MissingElementError("Audio element does not have 'src' attribute")

            src = audio.get('src')
            if not isinstance(src, str):
                raise UnexpectedElementError(f"Expected 'src' attribute to be a string, got {type(src)}")
            
            url = urljoin(base_url, src)

            parsed_url = urlparse(url)
            format_ext = parsed_url.path.split('.')[-1].lower()

            media = Media(
                media_type='audio',
                format=format_ext,
                src=src
            )
            media_list.append(media)

        return media_list
    
    def _parse_video(self, content_element: Tag, base_url: str) -> list[Media]:
        """
        Parses video elements from the content element and returns a list of Media objects.
        
        :param Tag content_element: The content element containing video tags.
        :param str base_url: The base URL to resolve relative video URLs.
        :return: A list of Media objects representing the video files.
        :rtype: list[Media]
        :raises MissingElementError: If no video elements are found or if a video element does not have 'src' attribute.
        :raises UnexpectedElementError: If a video element's 'src' attribute is not a string.
        """
        video_elements = VinewsValidator.validate_tags(
            elements=content_element.find_all('video')
        )

        media_list: list[Media] = []

        for video in video_elements:
            if not video.has_attr('src'):
                raise MissingElementError("Video element does not have 'src' attribute")

            src = video.get('src')
            if not isinstance(src, str):
                raise UnexpectedElementError(f"Expected 'src' attribute to be a string, got {type(src)}")
            
            url = urljoin(base_url, src)

            parsed_url = urlparse(url)
            format_ext = parsed_url.path.split('.')[-1].lower()

            media = Media(
                media_type='video',
                format=format_ext,
                src=src
            )
            media_list.append(media)

        return media_list
    
    def _parse_media(self, content_element: Tag, base_url: str) -> list[Media]:
        """
        Parses media elements (images, audio, videos) from the content element and returns a list of Media objects.

        :param Tag content_element: The content element containing media tags.
        :param str base_url: The base URL to resolve relative media URLs.
        :return: A list of Media objects representing the media files.
        :rtype: list[Media]
        :raises MissingElementError: If no media elements are found.
        :raises UnexpectedElementError: If a media element does not have the expected attributes or structure.
        """
        media_list: list[Media] = []

        try:
            images = self._parse_images(content_element, base_url)
            media_list.extend(images)
        except MissingElementError:
            pass
        except UnexpectedElementError as e:
            raise UnexpectedElementError(f"Error parsing images: {e}")

        try:
            audios = self._parse_audio(content_element, base_url)
            media_list.extend(audios)
        except MissingElementError:
            pass
        except UnexpectedElementError as e:
            raise UnexpectedElementError(f"Error parsing audios: {e}")

        try:
            videos = self._parse_video(content_element, base_url)
            media_list.extend(videos)
        except MissingElementError:
            pass
        except UnexpectedElementError as e:
            raise UnexpectedElementError(f"Error parsing videos: {e}")

        return media_list
    
    def _parse_related_news(self, content_element: Tag) -> list[NewsCard]:
        """
        Parses related news elements from the content element and returns a list of NewsCard objects.

        :param Tag content_element: The content element containing related news tags.
        :return: A list of NewsCard objects representing the related news.
        :rtype: list[NewsCard]
        :raises MissingElementError: If no related news elements are found.
        :raises UnexpectedElementError: If a related news element does not have the expected structure.
        """
        related_news_section = VinewsValidator.validate_tag(
            element=content_element.find('div', class_='box-tinlienquanv2')
        )

        related_news_elements = VinewsValidator.validate_tags(
            elements=related_news_section.find_all('article')
        )

        related_news: list[NewsCard] = []

        for related_news_element in related_news_elements:
            link_element = VinewsValidator.validate_tag(
                element=related_news_element.find('a', class_='thumb')
            )
            title_element = VinewsValidator.validate_tag(
                element=related_news_element.find('h4', class_='title-news')
            )
            description_element = related_news_element.find('p', class_='description')

            url = link_element.get('href')
            if not isinstance(url, str):
                raise UnexpectedElementError(f"Expected 'href' attribute to be a string, got {type(url)}")

            title = title_element.get_text(strip=True)
            description = description_element.get_text(strip=True) if description_element else ""

            related_news.append(
                NewsCard(
                    url=url,
                    title=title,
                    description=description,
                    domain="vnexpress.net"
                )
            )

        return related_news
    
    def _parse_comments(self, content_element: Tag) -> list[Comment]:
        """
        Parses comment elements from the content element and returns a list of Comment objects.

        :param Tag content_element: The content element containing comment tags.
        :return: A list of Comment objects representing the comments.
        :rtype: list[Comment]
        :raises MissingElementError: If no comment elements are found.
        :raises UnexpectedElementError: If a comment element does not have the expected structure.
        """
        comment_elements = VinewsValidator.validate_tags(
            elements=content_element.find_all('div', class_='content-comment')
        )

        comments: list[Comment] = []

        for comment in comment_elements:
            username_element = VinewsValidator.validate_tag(
                element=comment.find('a', class_='nickname')
            )
            full_content_element = VinewsValidator.validate_tag(
                element=comment.find('p', class_='full_content')
            )
            timestamp_element = VinewsValidator.validate_tag(
                element=comment.find('span', class_='time-com')
            )

            excluded_span = full_content_element.find('span', class_='txt-name')
            if excluded_span:
                excluded_span.extract()

            username = username_element.get_text(strip=True)
            content = full_content_element.get_text(strip=True)
            timestamp_text = timestamp_element.get_text(strip=True)
            timestamp = VinewsValidator.parse_vi_datetime_string(timestamp_text)

            comments.append(
                Comment(
                    username=username,
                    content=content,
                    timestamp=int(timestamp.timestamp())
                )
            )

        return comments
    
    def parse_article(self, url: str, response: str) -> Article:
        """
        Parses the VnExpress article response at the given URL and returns a structured output.

        :param str url: The URL of the VnExpress article for referencing in the Article object.
        :param str response: The HTML response content of the article.
        :return: An Article object containing the parsed data.
        :rtype: Article
        :raises InvalidURLError: If the provided URL is not a valid VnExpress article URL.
        :raises MissingElementError: If the article section or required elements are not found.
        :raises UnexpectedElementError: If an unexpected element type is encountered.
        """
        soup = BeautifulSoup(response, 'html.parser')

        article_section = VinewsValidator.validate_tag(
            element=soup.find('section', class_='top-detail')
        )

        title_element = article_section.find('h1', attrs={"class": "title-detail"})

        if not title_element:
            title_element = soup.find('title')

        title_element = VinewsValidator.validate_tag(title_element)
        
        title = title_element.get_text(strip=True)

        header_element = VinewsValidator.validate_tag(
            element=article_section.find('div', attrs={"class": "header-content"})
        )

        publish_date_element = header_element.find('span', attrs={"class": "date"})
        if not publish_date_element:
            raise MissingElementError("Publish date element not found in the header")
        
        publish_date_text: str = publish_date_element.get_text(strip=True)
        publish_date: datetime = VinewsValidator.parse_vi_datetime_string(publish_date_text)
        
        tags_ul_element = VinewsValidator.validate_tag(
            element=header_element.find('ul')
        )

        tags: Optional[list[str]] = [
            li.get_text(strip=True) 
            for li in tags_ul_element.find_all('li')
        ]

        description_element = VinewsValidator.validate_tag(
            element=article_section.find('p', attrs={"class": "description"})
        )

        description = description_element.get_text(strip=True)
        
        content_element = VinewsValidator.validate_tag(
            element=article_section.find('article', attrs={"class": "fck_detail"})
        )

        media: list[Media] = self._parse_media(
            content_element=content_element,
            base_url=url
        )

        content_md = markdownify.markdownify(str(content_element), heading_style="ATX") # type: ignore

        if not isinstance(content_md, str):
            raise UnexpectedElementError("Content element is not a valid string after markdown conversion")

        author_element = VinewsValidator.validate_tag(
            element=content_element.find('p', attrs={"style": re.compile(r'text-align\s*:\s*right\s*;?')})
        )

        author = author_element.get_text(strip=True)

        try:
            related_news: list[NewsCard] = self._parse_related_news(
                content_element=content_element
            )
        except MissingElementError:
            related_news = []

        bottom_section = VinewsValidator.validate_tag(
            element=soup.find('section', class_='bottom-detail')
        )

        try:
            comments: list[Comment] = self._parse_comments(
                content_element=bottom_section
            )
        except MissingElementError:
            comments = []

        return Article(
            url=url,
            domain="vnexpress.net",
            title=title,
            description=description,
            content=content_md,
            media=media,
            author=author,
            publish_timestamp=int(publish_date.timestamp()),
            tags=tags,
            related_news=related_news,
            comments=comments,
        )

class VinewsVnExpressPageParser(IVinewsPageParser):
    def __init__(self):
        self._homepage_url = "https://vnexpress.net/"
        self._domain = "vnexpress.net"

    def _parse_featured_article(self, featured_news_element: Tag) -> NewsCard:
        """
        Parses the featured article from the top news section and returns a NewsCard object.

        :param Tag featured_news_element: The HTML element containing the featured news.
        :return: A NewsCard object representing the featured news.
        :rtype: NewsCard
        :raises MissingElementError: If the featured news element or required attributes are not found.
        :raises UnexpectedElementError: If an unexpected element type is encountered.
        """
        title_element = featured_news_element.find('h2', class_='title-news') or featured_news_element.find('h3', class_='title-news')

        if not title_element:
            raise MissingElementError("Featured news element does not have a title")
        
        title_element = VinewsValidator.validate_tag(
            element=title_element
        )

        link_element = VinewsValidator.validate_tag(
            element=title_element.find('a')
        )

        url = link_element.get('href')

        if not url:
            raise MissingElementError("Featured news element does not have 'href' attribute")
        
        if not isinstance(url, str):
            raise UnexpectedElementError(f"Expected 'href' attribute to be a string, got {type(url)}")
        
        title = link_element.get_text(strip=True)

        description_elements = VinewsValidator.validate_tags(
            elements=featured_news_element.find_all('p')
        )

        description = '\n\n'.join(
            desc.get_text(strip=True) for desc in description_elements
        )

        return NewsCard(
            url=url,
            title=title,
            description=description,
            domain=self._domain
        )

    def _parse_top_news(self, soup: BeautifulSoup) -> TopNews:
        """
        Parses the top news section from the homepage soup and returns a TopNews object.

        :param BeautifulSoup soup: The BeautifulSoup object containing the homepage HTML.
        :return: A TopNews object containing the featured and sub-featured news.
        :rtype: TopNews
        :raises MissingElementError: If the top section or required elements are not found.
        :raises UnexpectedElementError: If an unexpected element type is encountered.
        """
        top_section = VinewsValidator.validate_tag(
            element=soup.find('section', class_='section_topstory')
        )

        featured_news_element = VinewsValidator.validate_tag(
            element=top_section.find('article', class_='article-topstory')
        )
        
        featured_news = self._parse_featured_article(featured_news_element)

        sub_featured_news_ul = VinewsValidator.validate_tag(
            element=top_section.find('ul', class_='list-sub-feature')
        )

        sub_featured_news_li = VinewsValidator.validate_tags(
            elements=sub_featured_news_ul.find_all('li')
        )

        sub_featured_news: list[NewsCard] = []

        for li in sub_featured_news_li:
            a_element = VinewsValidator.validate_tag(
                element=li.find('a')
            )
            url = a_element.get('href')
            title = a_element.get_text(strip=True)

            if not isinstance(url, str):
                raise UnexpectedElementError(f"Expected 'href' attribute to be a string, got {type(url)}")

            sub_featured_news.append(
                NewsCard(
                    url=url,
                    title=title,
                    description="",
                    domain=self._domain
                )
            )

        return TopNews(
            featured=featured_news,
            sub_featured=sub_featured_news,
            total_articles= len(sub_featured_news) + 1  # +1 for the featured news
        )
    
    def _parse_article_card(self, article: Tag) -> NewsCard:
        """
        Parses an article card from the homepage and returns a NewsCard object.

        :param Tag articale: The HTML element containing the article card.
        :return: A NewsCard object representing the article.
        :rtype: NewsCard
        :raises MissingElementError: If the article card does not have the required elements.
        :raises UnexpectedElementError: If an unexpected element type is encountered.
        """
        title_element = article.find('h3', class_='title-news') or article.find('h2', class_='title-news')

        if not title_element:
            raise MissingElementError("Article card does not have a title")

        title_element = VinewsValidator.validate_tag(
            element=title_element
        )

        link_element = VinewsValidator.validate_tag(
            element=title_element.find('a')
        )

        url = link_element.get('href')

        if not url:
            raise MissingElementError("Article card does not have 'href' attribute")
        
        if not isinstance(url, str):
            raise UnexpectedElementError(f"Expected 'href' attribute to be a string, got {type(url)}")
        
        title = link_element.get_text(strip=True)

        description_element = VinewsValidator.validate_tag(
            element=article.find('p', class_='description')
        )
        description = description_element.get_text(strip=True) if description_element else ""

        try:
            location_stamp = VinewsValidator.validate_tag(
                element=description_element.find('span', class_='location-stamp')
            ).get_text(strip=True)
        except MissingElementError:
            location_stamp = ""

        return NewsCard(
            url=url,
            title=title,
            description=description,
            domain=self._domain,
            tags=[location_stamp] if location_stamp else None
        )
    
    def _parse_categorized_news(self, soup: BeautifulSoup) -> list[CategorizedNews]:
        """
        Parses the categorized news sections from the homepage soup and returns a list of CategorizedNews objects.

        :param BeautifulSoup soup: The BeautifulSoup object containing the homepage HTML.
        :return: A list of CategorizedNews objects representing the categorized news.
        :rtype: list[CategorizedNews]
        :raises MissingElementError: If the category boxes or required elements are not found.
        :raises UnexpectedElementError: If an unexpected element type is encountered.
        """
        category_boxes = VinewsValidator.validate_tags(
            elements=soup.find_all('div', class_='box-category')
        )

        categorized_news: list[CategorizedNews] = []

        for box in category_boxes:
            try:
                category = VinewsValidator.validate_tag(
                    element=box.find('h2', attrs={"class": "parent-cate"})
                ).get_text(strip=True)
            except MissingElementError:
                continue

            content_box = VinewsValidator.validate_tag(
                element=box.find('div', class_='content-box-category')
            )

            articles = VinewsValidator.validate_tags(
                elements=content_box.find_all('article')
            )

            news_cards: list[NewsCard] = []

            for article in articles:
                title_element = VinewsValidator.validate_tag(
                    element=article.find('h3', class_='title-news')
                )

                link_element = VinewsValidator.validate_tag(
                    element=title_element.find('a')
                )

                url = link_element.get('href')

                if not url:
                    raise MissingElementError("Article element does not have 'href' attribute")
                if not isinstance(url, str):
                    raise UnexpectedElementError(f"Expected 'href' attribute to be a string, got {type(url)}")
                
                title = link_element.get_text(strip=True)

                description_element = article.find('p', class_='description')
                description = description_element.get_text(strip=True) if description_element else ""

                news_cards.append(
                    NewsCard(
                        url=url,
                        title=title,
                        description=description,
                        domain=self._domain
                    )
                )

            categorized_news.append(
                CategorizedNews(
                    category=category,
                    news_cards=news_cards,
                    total_articles=len(news_cards)
                )
            )
        
        return categorized_news

    def parse_homepage(self, response: str) -> Homepage:
        """
        Parses the VnExpress homepage and returns a structured Homepage object.
        
        :param str response: The HTML response content of the homepage.
        :return: A Homepage object containing the parsed data.
        :rtype: Homepage
        :raises MissingElementError: If the homepage does not contain the expected sections or elements.
        :raises UnexpectedElementError: If an unexpected element type is encountered.
        """
        soup = BeautifulSoup(response, 'html.parser')

        top_news = self._parse_top_news(soup)

        middle_section = VinewsValidator.validate_tag(
            element=soup.find('section', class_='section_stream_home')
        )

        latest_news_articles = VinewsValidator.validate_tags(
            elements=middle_section.find_all('article')
        )

        latest_news: list[NewsCard] = []

        for article in latest_news_articles:
            try:
                latest_news.append(self._parse_article_card(article))
            except MissingElementError:
                continue # Skip articles that do not have the required elements

        categorized_news = self._parse_categorized_news(soup)

        total_categorized_news = sum(cat.total_articles for cat in categorized_news)

        return Homepage(
            url=self._homepage_url,
            domain=self._domain,
            top_news=top_news,
            latest_news=latest_news,
            categorized_news=categorized_news,
            total_articles=len(latest_news) + top_news.total_articles + total_categorized_news,
            timestamp=int(datetime.now().timestamp())
        )
    
    def parse_topic(self, response: str) -> TopicPage:
        """
        Parses a VnExpress topic page and returns a structured TopicPage object.

        :param str response: The HTML response content of the topic page.
        :return: A TopicPage object containing the parsed data.
        :rtype: TopicPage
        :raises MissingElementError: If the topic section or required elements are not found.
        :raises UnexpectedElementError: If an unexpected element type is encountered.
        """
        soup = BeautifulSoup(response, 'html.parser')

        topic = VinewsValidator.validate_tag(
            element=soup.find('div', class_='title-folder')
        ).get_text(strip=True)

        sub_topic_ul = VinewsValidator.validate_tag(
            element=soup.find('ul', class_='ul-nav-folder')
        )

        sub_topic = VinewsValidator.validate_tag(
            element=sub_topic_ul.find('li', class_='active')
        ).get_text(strip=True)

        main_section = VinewsValidator.validate_tag(
            element=soup.find('section', class_='section_container')
        )

        featured_news_element = VinewsValidator.validate_tag(
            element=main_section.find('article', class_='article-topstory')
        )

        featured_news = self._parse_featured_article(featured_news_element)

        latest_news_section = VinewsValidator.validate_tag(
            element=main_section.find('div', class_='list-news-subfolder')
        )

        latest_news_articles = VinewsValidator.validate_tags(
            elements=latest_news_section.find_all('article')
        )

        latest_news: list[NewsCard] = []

        for article in latest_news_articles:
            try:
                latest_news.append(self._parse_article_card(article))
            except MissingElementError:
                continue

        return TopicPage(
            url=self._homepage_url,
            domain=self._domain,
            topic=topic,
            sub_topic=sub_topic,
            featured_news=featured_news,
            latest_news=latest_news,
            total_articles=len(latest_news) + 1,  # +1 for the featured news
            timestamp=int(datetime.now().timestamp())
        )
    
    def parse_search_results(self, response: str) -> list[NewsCard]:
        """
        Parses the VnExpress search results page and returns a list of NewsCard objects.

        :param str response: The HTML response content of the search results page.
        :return: A list of NewsCard objects representing the search results.
        :rtype: list[NewsCard]
        :raises MissingElementError: If the search results section or required elements are not found.
        :raises UnexpectedElementError: If an unexpected element type is encountered.
        """
        soup = BeautifulSoup(response, 'html.parser')

        search_results_section = VinewsValidator.validate_tag(
            element=soup.find('div', id='result_search')
        )

        search_results_articles = VinewsValidator.validate_tags(
            elements=search_results_section.find_all('article')
        )

        search_results: list[NewsCard] = []

        for article in search_results_articles:
            try:
                search_results.append(self._parse_article_card(article))
            except MissingElementError:
                continue  # Skip articles that do not have the required elements

        return search_results
    