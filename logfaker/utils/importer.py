"""CSV import utilities."""

import csv
import json
from pathlib import Path
from typing import List, Optional, Union

from logfaker.core.config import GeneratorConfig
from logfaker.core.models import Category, Content, UserProfile


class CsvImporter:
    """Handles importing data from CSV files."""

    @staticmethod
    def import_content(input_path: Union[str, Path]) -> Optional[List[Content]]:
        """Import content from CSV."""
        try:
            contents = []
            with open(input_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    content = Content(
                        content_id=int(row["Content ID"]),
                        title=row["Title"],
                        description=row["Description"],
                        category=row["Category"]
                    )
                    contents.append(content)
            return contents
        except (FileNotFoundError, KeyError):
            return None

    @staticmethod
    def import_users(input_path: Union[str, Path], categories: Optional[List[Category]] = None) -> Optional[List[UserProfile]]:
        """Import user profiles from CSV."""
        try:
            users = []
            with open(input_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    preferences = row["Preferences"].split(", ")
                    if categories:
                        from logfaker.generators.users import UserGenerator
                        generator = UserGenerator(GeneratorConfig(api_key="dummy"))
                        preferences = generator.validate_preferences(preferences, categories)
                    user = UserProfile(
                        user_id=int(row["User ID"]),
                        brief_explanation=row["Brief Explanation"],
                        profession=row["Profession"],
                        preferences=preferences
                    )
                    users.append(user)
            return users
        except (FileNotFoundError, KeyError):
            return None
