"""Query generation based on user profiles and content."""

from typing import List, Optional

from openai import OpenAI

from logfaker.core.config import GeneratorConfig
from logfaker.core.models import SearchQuery, UserProfile


class QueryGenerator:
    """Generates search queries based on user profiles."""

    def __init__(self, config: GeneratorConfig):
        """Initialize the query generator."""
        self.config = config
        self.client = OpenAI(api_key=config.api_key)

    def generate_query(self, user: UserProfile) -> SearchQuery:
        """
        Generate a single search query for a user.

        Args:
            user: UserProfile to base the query on

        Returns:
            SearchQuery object
        """
        prompt = self._create_query_prompt(user)
        response = self.client.chat.completions.create(
            model=self.config.ai_model,
            messages=[
                {"role": "system", "content": "You are a search query generator."},
                {"role": "user", "content": prompt},
            ],
        )

        # Use first preference as a simple query
        return SearchQuery(
            query_id=1,  # Will be replaced with actual ID generation
            user_id=user.user_id,
            query_content=user.preferences[0] if user.preferences else "general",
            category="General",
        )

    def generate_queries(self, user: UserProfile, count: int) -> List[SearchQuery]:
        """
        Generate multiple search queries for a user.

        Args:
            user: UserProfile to base queries on
            count: Number of queries to generate

        Returns:
            List of SearchQuery objects
        """
        return [self.generate_query(user) for _ in range(count)]

    def _create_query_prompt(self, user: UserProfile) -> str:
        """Create a prompt for query generation based on user profile."""
        return (
            f"Generate a simple one or two word search query based on: "
            f"{', '.join(user.preferences)}"
        )
