"""Data models for Logfaker."""

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


class Category(BaseModel):
    """Model for content categories."""

    id: int = Field(description="Unique identifier for the category")
    name: str = Field(description="Category name")
    description: str = Field(description="Category description")


class Content(BaseModel):
    """Model for content in library catalog."""

    content_id: int = Field(description="Unique identifier for the content")
    title: str = Field(description="Title of the content")
    description: str = Field(description="Description or summary of the content")
    category: str = Field(description="Primary category of the content")


class UserProfile(BaseModel):
    """Model for virtual user profiles."""

    user_id: int = Field(description="Unique identifier for the user")
    brief_explanation: str = Field(
        description="Brief description of the user's background and interests"
    )
    profession: str = Field(description="Professional occupation of the user")
    preferences: List[str] = Field(
        description="List of user's interests and preferences"
    )


class SearchQuery(BaseModel):
    """Model for search queries."""

    query_id: int = Field(description="Unique identifier for the query")
    user_id: int = Field(description="ID of the user who made the query")
    query_content: str = Field(description="The actual search query text")
    category: str = Field(description="Category of the search query")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SearchResult(BaseModel):
    """Model for search results."""

    content_id: int = Field(description="ID of the content in results")
    title: str = Field(description="Title of the content")
    relevance_score: Optional[float] = Field(None, description="Search relevance score")


class SearchLog(BaseModel):
    """Model for complete search log entries."""

    query_id: int = Field(description="ID of the search query")
    user_id: int = Field(description="ID of the user who made the query")
    search_query: str = Field(description="The search query text")
    search_results: List[SearchResult] = Field(description="List of search results")
