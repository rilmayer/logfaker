"""Virtual user generation using AI."""

import json
import logging
import random
from pathlib import Path
from typing import List, Optional, Union

from openai import OpenAI

from logfaker.core.config import GeneratorConfig
from logfaker.core.models import UserProfile
from logfaker.generators.content import ContentGenerator
from logfaker.utils.importer import CsvImporter


class UserGenerator:
    """Generates virtual user profiles using AI."""

    def __init__(self, config: GeneratorConfig):
        """Initialize the user generator."""
        self.config = config
        self.client = OpenAI(api_key=config.api_key)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, config.log_level))
        self.content_generator = ContentGenerator(config)

    def validate_preferences(
        self, preferences: List[str], category_names: List[str]
    ) -> List[str]:
        """Validate and filter preferences to match category names."""
        valid_preferences = [pref for pref in preferences if pref in category_names]
        if not valid_preferences:
            self.logger.warning("No valid preferences found, using first category")
            valid_preferences = [category_names[0]]
        else:
            invalid = set(preferences) - set(category_names)
            if invalid:
                self.logger.warning(f"Filtered out invalid preferences: {invalid}")
        return valid_preferences

    def generate_user(self, user_id: int = 1) -> UserProfile:
        """
        Generate a single user profile with interests.

        Args:
            user_id: Unique identifier for the user

        Returns:
            UserProfile object with generated data
        """
        self.logger.info(
            "Generating user profile %d for %s", user_id, self.config.service_type
        )
        categories = self.content_generator._load_or_generate_categories()
        category_names = [cat.name for cat in categories]
        functions = [
            {
                "name": "create_user",
                "description": "Create user profile",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "brief_explanation": {
                            "type": "string",
                            "description": (
                                "Brief explanation of the user's interests and how they use "
                                "the search service."
                            ),
                        },
                        "profession": {
                            "type": "string",
                            "description": "User's profession",
                        },
                        "preferences": {
                            "type": "array",
                            "items": {"type": "string", "enum": category_names},
                            "minItems": 1,
                            "description": (
                                f"Must be one of: " f"{', '.join(category_names)}"
                            ),
                        },
                    },
                    "required": ["brief_explanation", "profession", "preferences"],
                },
            }
        ]
        self.logger.debug("Available categories: %s", ", ".join(category_names))
        response = self.client.chat.completions.create(
            model=self.config.ai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Generate a brief third-person introduction of a user profile explaining "
                        f"how they use '{self.config.service_type}' in {self.config.language}. "
                        f"User is interested in {random.choice(category_names)}."
                    ),
                }
            ],
            functions=functions,
            function_call={"name": "create_user"},
        )

        # Parse response and handle potential JSON parsing issues
        try:
            args_str = response.choices[0].message.function_call.arguments
            self.logger.debug("Raw response arguments: %s", args_str)
            self.logger.debug("Response type: %s", type(args_str))
            self.logger.debug("Response repr: %s", repr(args_str))

            result = json.loads(args_str)
            self.logger.debug("Parsed response: %s", result)
            self.logger.debug("Result type: %s", type(result))
            self.logger.debug("Result keys: %s", list(result.keys()))

            preferences = self.validate_preferences(
                result["preferences"], category_names
            )
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.error("Failed to parse response: %s", e)
            self.logger.error("Response type: %s", type(args_str))
            self.logger.error("Response repr: %s", repr(args_str))
            raise

        user = UserProfile(
            user_id=user_id,
            brief_explanation=result["brief_explanation"],
            profession=result["profession"],
            preferences=preferences,
        )

        self.logger.info(
            "Generated user %d with %d interests", user_id, len(user.preferences)
        )
        self.logger.debug("User interests: %s", ", ".join(user.preferences))
        return user

    def generate_users(
        self,
        count: int,
        reuse_file: bool = True,
        csv_path: Optional[Union[str, Path]] = None,
    ) -> List[UserProfile]:
        """
        Generate multiple user profiles.

        Args:
            count: Number of users to generate
            reuse_file: If True, try to load from users.csv first
            csv_path: Optional path to users.csv file. If not provided,
                uses output_dir/users.csv or users.csv

        Returns:
            List of UserProfile objects
        """
        if reuse_file:
            # Try output_dir first if no specific path provided
            has_output_dir = (
                csv_path is None
                and hasattr(self.config, "output_dir")
                and self.config.output_dir
            )
            if has_output_dir:
                csv_path = self.config.output_dir / "users.csv"
                if csv_path.exists():
                    self.logger.info("Checking output directory: %s", csv_path)
                    categories = self.content_generator._load_or_generate_categories()
                    users = CsvImporter.import_users(csv_path, categories)
                    if users and len(users) >= count:
                        self.logger.info("Reusing %d profiles from %s", count, csv_path)
                        return users[:count]

            # Fall back to default behavior
            file_path = Path(csv_path if csv_path else "users.csv").resolve()
            self.logger.debug("Looking for users file at: %s", file_path)
            categories = self.content_generator._load_or_generate_categories()
            users = CsvImporter.import_users(file_path, categories)
            if users and len(users) >= count:
                self.logger.info("Reusing %d profiles from %s", count, file_path)
                return users[:count]
        self.logger.info("Generating %d user profiles", count)
        users = [self.generate_user(i + 1) for i in range(count)]
        self.logger.info("Generated %d user profiles", len(users))
        return users
