"""Query generation based on user profiles and content."""

import json
import logging
import random
from typing import List

from openai import OpenAI

from logfaker.core.config import GeneratorConfig
from logfaker.core.models import SearchQuery, UserProfile


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
        self.logger.info(
            f"Generating query for user {user.user_id} with interests: {', '.join(user.preferences)}"
        )

        functions = [
            {
                "name": "create_query",
                "description": "Create an assumed realistic search keyword based on user interests",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_content": {
                            "type": "string",
                            "description": "Search keyword",
                        },
                        "category": {
                            "type": "string",
                            "description": "Theme of the search keyword based on the user needs",
                        },
                    },
                    "required": ["query_content", "category"],
                },
            }
        ]

        response = self.client.chat.completions.create(
            model=self.config.ai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Generate a search query in {self.config.language}. "
                        f"User interests: {random.choice(user.preferences)}. "
                        f"User background: {user.brief_explanation}"
                    ),
                }
            ],
            functions=functions,
            function_call={"name": "create_query"},
        )

        result = json.loads(response.choices[0].message.function_call.arguments)
        query = SearchQuery(
            query_id=query_id,
            user_id=user.user_id,
            query_content=result["query_content"],
            category=result["category"],
        )

        self.logger.info(
            f"Generated query: {query.query_content} (category: {query.category})"
        )
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
            f"Generate a search query in {self.config.language}. "
            f"User interests: {random.choice(user.preferences)}. "
            f"User background: {user.brief_explanation}"
        )
