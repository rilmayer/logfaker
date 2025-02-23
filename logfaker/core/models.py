"""Data models for Logfaker."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class BookContent(BaseModel):
    """Model for book content in library catalog."""

    content_id: int = Field(description="Unique identifier for the content")
    title: str = Field(description="Title of the book")
    description: str = Field(description="Description or summary of the book")
    category: str = Field(description="Primary category of the book")
    author: Optional[str] = Field(None, description="Author of the book")
    publisher: Optional[str] = Field(None, description="Publisher of the book")
    year: Optional[int] = Field(None, description="Publication year")
    genre: Optional[str] = Field(None, description="Genre of the book")
    abstract: Optional[str] = Field(None, description="Detailed abstract of the book")


class UserProfile(BaseModel):
    """Model for virtual user profiles."""

    user_id: int = Field(description="Unique identifier for the user")
    age: int = Field(description="Age of the user")
    gender: str = Field(description="Gender of the user")
    profession: str = Field(description="Professional occupation of the user")
    preferences: List[str] = Field(
        description="List of user's interests and preferences"
    )

    def to_json_str(self) -> str:
        """Convert user attributes to JSON string for CSV output."""
        return {
            "age": self.age,
            "gender": self.gender,
            "profession": self.profession,
        }.__str__()


class SearchQuery(BaseModel):
    """Model for search queries."""

    query_id: int = Field(description="Unique identifier for the query")
    user_id: int = Field(description="ID of the user who made the query")
    query_content: str = Field(description="The actual search query text")
    category: str = Field(description="Category of the search query")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SearchResult(BaseModel):
    """Model for search results."""

    content_id: int = Field(description="ID of the content in results")
    title: str = Field(description="Title of the content")
    url: str = Field(description="URL to the content")
    relevance_score: Optional[float] = Field(None, description="Search relevance score")


class SearchLog(BaseModel):
    """Model for complete search log entries."""

    query_id: int = Field(description="ID of the search query")
    user_id: int = Field(description="ID of the user who made the query")
    search_query: str = Field(description="The search query text")
    search_results: List[SearchResult] = Field(description="List of search results")
    clicks: Optional[int] = Field(None, description="Number of result clicks")
    ctr: Optional[float] = Field(None, description="Click-through rate")
