"""Base search engine interface."""
from abc import ABC, abstractmethod
from typing import List, Optional

from logfaker.core.models import SearchResult


class SearchEngine(ABC):
    """Abstract base class for search engine implementations."""

    @abstractmethod
    def search(
        self,
        query: str,
        max_results: int = 10,
        category: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Execute a search query and return results.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            category: Optional category to filter results

        Returns:
            List of SearchResult objects
        """
        pass

    @abstractmethod
    def index_content(self, content_id: int, data: dict) -> bool:
        """
        Index new content in the search engine.

        Args:
            content_id: Unique identifier for the content
            data: Content data to index

        Returns:
            True if indexing was successful
        """
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """
        Check if the search engine is healthy and responsive.

        Returns:
            True if the search engine is healthy
        """
        pass
