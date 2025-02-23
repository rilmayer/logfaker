"""CSV import utilities."""

import csv
import json
from pathlib import Path
from typing import List, Optional, Union

from logfaker.core.models import Content, UserProfile


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
    def import_users(input_path: Union[str, Path]) -> Optional[List[UserProfile]]:
        """Import user profiles from CSV."""
        try:
            users = []
            with open(input_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    user = UserProfile(
                        user_id=int(row["User ID"]),
                        brief_explanation=row["Brief Explanation"],
                        profession=row["Profession"],
                        preferences=row["Preferences"].split(", ")
                    )
                    users.append(user)
            return users
        except (FileNotFoundError, KeyError):
            return None
