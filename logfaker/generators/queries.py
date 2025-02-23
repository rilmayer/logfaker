"""Query generation based on user profiles and content."""

import json
import logging
from typing import List, Optional

from openai import OpenAI

from logfaker.core.config import GeneratorConfig
from logfaker.core.models import SearchQuery, SearchResult, UserProfile


class QueryGenerator:
    """Generates search queries based on user profiles."""

    def __init__(self, config: GeneratorConfig):
        """Initialize the query generator."""
        self.config = config
        self.client = OpenAI(api_key=config.api_key)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, config.log_level))

    def generate_query(self, user: UserProfile, query_id: int = 1) -> SearchQuery:
        """
        Generate a single search query for a user.

        Args:
            user: UserProfile to base the query on
            query_id: Unique identifier for the query

        Returns:
            SearchQuery object
        """
        self.logger.info(f"Generating query for user {user.user_id} with interests: {', '.join(user.preferences)}")
        
        functions = [{
            "name": "create_query",
            "description": "Create search query based on user interests",
            "parameters": {
                "type": "object",
                "properties": {
                    "query_content": {"type": "string"},
                    "category": {"type": "string"}
                },
                "required": ["query_content", "category"]
            }
        }]

        response = self.client.chat.completions.create(
            model=self.config.ai_model,
            messages=[{
                "role": "system",
                "content": (
                    f"Generate a search query for {self.config.service_type} in {self.config.language}. "
                    f"User interests: {', '.join(user.preferences)}. "
                    f"User background: {user.brief_explanation}"
                )
            }],
            functions=functions,
            function_call={"name": "create_query"}
        )

        result = json.loads(response.choices[0].message.function_call.arguments)
        query = SearchQuery(
            query_id=query_id,
            user_id=user.user_id,
            query_content=result["query_content"],
            category=result["category"]
        )
        
        self.logger.info(f"Generated query: {query.query_content} (category: {query.category})")
        return query

    def generate_queries(self, user: UserProfile, count: int) -> List[SearchQuery]:
        """
        Generate multiple search queries for a user.

        Args:
            user: UserProfile to base queries on
            count: Number of queries to generate

        Returns:
            List of SearchQuery objects
        """
        self.logger.info(f"Generating {count} queries for user {user.user_id}")
        queries = [self.generate_query(user, i + 1) for i in range(count)]
        self.logger.info(f"Generated {len(queries)} queries")
        return queries

    def _create_query_prompt(self, user: UserProfile) -> str:
        """Create a prompt for query generation based on user profile."""
        return (
            f"Generate a search query for {self.config.service_type} in {self.config.language}. "
            f"User interests: {', '.join(user.preferences)}. "
            f"User background: {user.brief_explanation}"
        )

    def simulate_engagement(self, user: UserProfile, results: List[SearchResult]) -> tuple[int, float]:
        """
        Simulate user engagement with search results.

        Args:
            user: UserProfile to base simulation on
            results: List of search results to simulate engagement with

        Returns:
            Tuple of (clicks, ctr) where:
            - clicks is the number of results clicked (0-5)
            - ctr is the click-through rate (0.0-1.0)
        """
        self.logger.info(f"Simulating engagement for user {user.user_id} with {len(results)} results")
        
        # Make simulation deterministic per user
        import random
        random.seed(user.user_id)
        
        # Simulate clicks (0-5, not exceeding number of results)
        clicks = random.randint(0, min(5, len(results)))
        
        # Calculate CTR (0.0-1.0)
        ctr = clicks / len(results) if results else 0.0
        
        self.logger.info(f"Simulated engagement: {clicks} clicks, {ctr:.2f} CTR")
        return clicks, ctr
