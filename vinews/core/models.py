from vinews.core.utils import VinewsValidator
from pydantic import BaseModel, Field, model_validator
from typing import Any, Optional, Literal

class Comment(BaseModel):
    username: str
    content: str
    timestamp: int

class Media(BaseModel):
    media_type: Literal['image', 'video', 'audio']
    format: str
    src: str
    description: Optional[str] = None

class NewsCard(BaseModel):
    url: str
    title: str
    description: Optional[str] = None
    domain: str
    campaign: Optional[str] = None
    tags: Optional[list[str]] = None

    def __repr__(self) -> str:
        return (
            f"NewsCard(url={self.url}, title={self.title}, "
            f"description={str(self.description)[:100]}..., "
            f"domain={self.domain}), campaign={self.campaign})"
            f"tags={self.tags})"
        )
    
class Article(BaseModel):
    url: str
    domain: str
    title: str
    description: str
    content: str
    media: Optional[list[Media]] = None
    author: Optional[str] = None
    publish_timestamp: Optional[int] = None
    tags: list[str] = Field(default_factory=list)
    related_news: Optional[list[NewsCard]] = None
    comments: Optional[list[Comment]] = None

    @model_validator(mode='before')
    @classmethod
    def check_url_domain(cls, data: dict[str, Any]) -> dict[str, Any]:
        if not VinewsValidator.validate_url_with_domain(data['url'], data['domain']):
            raise ValueError(f"Invalid URL: {data['url']} for domain: {data['domain']}")
        return data

    def add_tag(self, tag: str) -> None:
        if tag not in self.tags:
            self.tags.append(tag)

    def __repr__(self) -> str:
        return (
            f"Article(url={self.url}, domain={self.domain}, title={self.title}, "
            f"description={self.description}, content={self.content[:100]}..., "
            f"author={self.author}, publish_timestamp={self.publish_timestamp}, tags={self.tags})"
        )
    
class CategorizedNews(BaseModel):
    category: str
    news_cards: list[NewsCard]
    total_articles: int

class TopNews(BaseModel):
    featured: NewsCard
    sub_featured: list[NewsCard]
    total_articles: int

class Homepage(BaseModel):
    url: str
    domain: str
    top_news: TopNews
    latest_news: list[NewsCard]
    categorized_news: list[CategorizedNews]
    total_articles: int
    timestamp: int

class CategorizedNewsArticles(BaseModel):
    category: str
    articles: list[Article]
    total_articles: int

class TopNewsArticles(BaseModel):
    featured: Optional[Article] = None
    sub_featured: list[Article]
    total_articles: int

class HomepageArticles(BaseModel):
    url: str
    domain: str
    top_news: TopNewsArticles
    latest_news: list[Article]
    categorized_news: list[CategorizedNewsArticles]
    total_articles: int
    timestamp: int

class TopicPage(BaseModel):
    url: str
    domain: str
    topic: str
    sub_topic: str
    featured_news: NewsCard
    latest_news: list[NewsCard]
    total_articles: int
    timestamp: int

    @model_validator(mode='before')
    @classmethod
    def check_url_domain(cls, data: dict[str, Any]) -> dict[str, Any]:
        if not VinewsValidator.validate_url_with_domain(data['url'], data['domain']):
            raise ValueError(f"Invalid URL: {data['url']} for domain: {data['domain']}")
        return data
    
class SearchResults(BaseModel):
    url: str
    domain: str
    params: dict[str, Any]
    results: list[NewsCard]
    total_results: int
    timestamp: int

    @model_validator(mode='before')
    @classmethod
    def check_url_domain(cls, data: dict[str, Any]) -> dict[str, Any]:
        if not VinewsValidator.validate_url_with_domain(data['url'], data['domain']):
            raise ValueError(f"Invalid URL: {data['url']} for domain: {data['domain']}")
        return data
    
class SearchResultsArticles(BaseModel):
    url: str
    domain: str
    params: dict[str, Any]
    results: list[Article]
    total_results: int
    timestamp: int

    @model_validator(mode='before')
    @classmethod
    def check_url_domain(cls, data: dict[str, Any]) -> dict[str, Any]:
        if not VinewsValidator.validate_url_with_domain(data['url'], data['domain']):
            raise ValueError(f"Invalid URL: {data['url']} for domain: {data['domain']}")
        return data