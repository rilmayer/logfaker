"""Virtual user generation using AI."""

import json
import logging
import random
from pathlib import Path
from typing import List, Optional, Union

from openai import OpenAI

from logfaker.core.config import GeneratorConfig
from logfaker.core.models import Category, UserProfile
from logfaker.utils.importer import CsvImporter


class UserGenerator:
    """Generates virtual user profiles using AI."""

    def __init__(self, config: GeneratorConfig):
        """Initialize the user generator."""
        self.config = config
        self.client = OpenAI(api_key=config.api_key)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, config.log_level))

    def validate_preferences(self, preferences: List[str], categories: List[Category]) -> List[str]:
        """Validate and filter preferences to match category names."""
        category_names = [cat.name for cat in categories]
        valid_preferences = [pref for pref in preferences if pref in category_names]
        if not valid_preferences:
            self.logger.warning("No valid preferences found, using first category")
            valid_preferences = [category_names[0]]
        else:
            invalid = set(preferences) - set(category_names)
            if invalid:
                self.logger.warning(f"Filtered out invalid preferences: {invalid}")
        return valid_preferences

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
        
        category_names = [cat.name for cat in categories]
        
        functions = [{
            "name": "create_user",
            "description": "Create user profile",
            "parameters": {
                "type": "object",
                "properties": {
                    "brief_explanation": {"type": "string", "description": "Brief explanation of the user's interests and how they use the search service."},
                    "profession": {"type": "string", "description": "User's profession"},
                    "preferences": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": category_names
                        },
                        "minItems": 1,
                        "description": f"Must be one of: {', '.join(category_names)}"
                    }
                },
                "required": ["brief_explanation", "profession", "preferences"]
            }
        }]
        self.logger.debug(f"Available categories: {', '.join(category_names)}")
        
        response = self.client.chat.completions.create(
            model=self.config.ai_model,
            messages=[{
                "role": "system",
                "content": (
                    f"Generate a brief third-person introduction of a user profile explaining how they use '{self.config.service_type}' in {self.config.language}."
                    f"User is interested in {random.choice(category_names)}."
                )
            }],
            functions=functions,
            function_call={"name": "create_user"}
        )

        result = json.loads(response.choices[0].message.function_call.arguments)
        preferences = self.validate_preferences(result["preferences"], categories)
        
        user = UserProfile(
            user_id=user_id,
            brief_explanation=result["brief_explanation"],
            profession=result["profession"],
            preferences=preferences
        )
        
        self.logger.info(f"Generated user {user_id} with {len(user.preferences)} interests")
        self.logger.debug(f"User interests: {', '.join(user.preferences)}")
        return user

    def generate_users(self, count: int, categories: List[Category], reuse_file: bool = True,
                      csv_path: Optional[Union[str, Path]] = None) -> List[UserProfile]:
        """
        Generate multiple user profiles.

        Args:
            count: Number of users to generate
            categories: List of available categories to choose interests from
            reuse_file: If True, try to load from users.csv first
            csv_path: Optional path to users.csv file. If not provided, uses "users.csv" in current directory

        Returns:
            List of UserProfile objects
        """
        if reuse_file:
            file_path = Path(csv_path if csv_path else "users.csv").resolve()
            self.logger.debug(f"Looking for users file at: {file_path}")
            users = CsvImporter.import_users(file_path, categories)
            if users and len(users) >= count:
                self.logger.info(f"Reusing {count} profiles from {file_path}")
                return users[:count]
        self.logger.info(f"Generating {count} user profiles")
        users = [self.generate_user(categories, i + 1) for i in range(count)]
        self.logger.info(f"Generated {len(users)} user profiles")
        return users
