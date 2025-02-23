"""Virtual user generation using AI."""

import json
import logging
from typing import List, Optional

from openai import OpenAI

from logfaker.core.config import GeneratorConfig
from logfaker.core.models import Category, UserProfile


class UserGenerator:
    """Generates virtual user profiles using AI."""

    def __init__(self, config: GeneratorConfig):
        """Initialize the user generator."""
        self.config = config
        self.client = OpenAI(api_key=config.api_key)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, config.log_level))

    def generate_user(self, categories: List[Category], user_id: int = 1) -> UserProfile:
        """
        Generate a single user profile with interests from categories.

        Args:
            categories: List of available categories to choose interests from
            user_id: Unique identifier for the user

        Returns:
            UserProfile object with generated data
        """
        self.logger.info(f"Generating user profile {user_id} for {self.config.service_type}")
        
        functions = [{
            "name": "create_user",
            "description": "Create user profile",
            "parameters": {
                "type": "object",
                "properties": {
                    "brief_explanation": {"type": "string"},
                    "profession": {"type": "string"},
                    "preferences": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1
                    }
                },
                "required": ["brief_explanation", "profession", "preferences"]
            }
        }]

        category_names = [cat.name for cat in categories]
        self.logger.debug(f"Available categories: {', '.join(category_names)}")
        
        response = self.client.chat.completions.create(
            model=self.config.ai_model,
            messages=[{
                "role": "system",
                "content": (
                    f"Generate a user profile for {self.config.service_type}. "
                    f"Select interests from categories: {category_names}. "
                    f"User must be interested in at least one category."
                )
            }],
            functions=functions,
            function_call={"name": "create_user"}
        )

        result = json.loads(response.choices[0].message.function_call.arguments)
        user = UserProfile(
            user_id=user_id,
            brief_explanation=result["brief_explanation"],
            profession=result["profession"],
            preferences=result["preferences"]
        )
        
        self.logger.info(f"Generated user {user_id} with {len(user.preferences)} interests")
        self.logger.debug(f"User interests: {', '.join(user.preferences)}")
        return user

    def generate_users(self, count: int, categories: List[Category]) -> List[UserProfile]:
        """
        Generate multiple user profiles.

        Args:
            count: Number of users to generate
            categories: List of available categories to choose interests from

        Returns:
            List of UserProfile objects
        """
        self.logger.info(f"Generating {count} user profiles")
        users = [self.generate_user(categories, i + 1) for i in range(count)]
        self.logger.info(f"Generated {len(users)} user profiles")
        return users
