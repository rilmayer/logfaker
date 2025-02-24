"""Content generation using AI."""

import json
import logging
from pathlib import Path
from typing import List, Optional, Union

from openai import OpenAI

from logfaker.core.config import GeneratorConfig
from logfaker.core.exceptions import ContentGenerationError
from logfaker.core.models import Category, Content
from logfaker.utils.csv import CsvExporter
from logfaker.utils.importer import CsvImporter


class ContentGenerator:
    """Generates content using AI."""

    def __init__(self, config: GeneratorConfig):
        """Initialize the content generator."""
        self.config = config
        self.client = OpenAI(api_key=config.api_key)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, config.log_level))
        self._categories: Optional[List[Category]] = None

    def _generate_categories(
        self, existing_names: Optional[set[str]] = None
    ) -> List[Category]:
        """
        Generate categories using function calling.

        Args:
            existing_names: Set of category names to avoid duplicates

        Returns:
            List of Category objects
        """
        functions = [
            {
                "name": "create_categories",
                "description": "Create categories for the search service",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "categories": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                },
                                "required": ["name", "description"],
                            },
                        }
                    },
                    "required": ["categories"],
                },
            }
        ]

        response = self.client.chat.completions.create(
            model=self.config.ai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Generate approximately 100 categories for {self.config.service_type} in {self.config.language}. "
                        f"Categories should be diverse and cover all potential content types.\n\n"
                        + (
                            f"IMPORTANT: The following categories already exist. You MUST NOT generate any categories that are similar to these:\n"
                            f"{', '.join(f'- {name}' for name in existing_names)}\n\n"
                            f"Generate completely different categories that cover other areas not mentioned above."
                            if existing_names
                            else ""
                        )
                    ),
                }
            ],
            functions=functions,
            function_call={"name": "create_categories"},
        )

        result = json.loads(response.choices[0].message.function_call.arguments)
        categories = []
        for cat in result["categories"]:
            if not existing_names or cat["name"] not in existing_names:
                categories.append(Category(id=0, **cat))  # ID will be assigned later
                if existing_names is not None:
                    existing_names.add(cat["name"])
        return categories

    def _generate_content_for_category(
        self, category: Category, content_id: int
    ) -> Content:
        """
        Generate a single content entry using function calling.

        Args:
            category: Category to generate content for
            content_id: Unique identifier for the content

        Returns:
            Content object with generated data
        """
        functions = [
            {
                "name": "create_content",
                "description": "Create content item",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                    },
                    "required": ["title", "description"],
                },
            }
        ]

        response = self.client.chat.completions.create(
            model=self.config.ai_model,
            messages=[
                {
                    "role": "system",
                    "content": f"Generate content for category '{category.name}' ({category.description}) in {self.config.service_type}. Use {self.config.language} language. Be careful that the generated content does not overlap with actual content in the real world.",
                }
            ],
            functions=functions,
            function_call={"name": "create_content"},
        )

        result = json.loads(response.choices[0].message.function_call.arguments)
        return Content(
            content_id=content_id,
            title=result["title"],
            description=result["description"],
            category=category.name,
        )

    def _load_or_generate_categories(self, min_count: int = 100) -> List[Category]:
        """Load categories from CSV or generate new ones."""
        if self._categories is not None:
            if len(self._categories) >= min_count:
                return self._categories

        # Try loading from CSV
        if self.config.output_dir:
            csv_path = self.config.output_dir / "categories.csv"
            if csv_path.exists():
                categories = CsvImporter.import_categories(csv_path)
                if categories and len(categories) >= min_count:
                    self._categories = categories
                    return categories
        else:
            self.logger.warning(
                "No output_dir configured, categories will not be persisted"
            )

        # Generate new categories
        existing_names = (
            set() if not self._categories else {c.name for c in self._categories}
        )
        categories = self._categories or []

        # Keep generating until we have enough unique categories
        while len(categories) < min_count:
            new_categories = self._generate_categories(existing_names)
            categories.extend(new_categories)

        # Assign IDs and export
        for i, cat in enumerate(categories):
            cat.id = i + 1

        if self.config.output_dir:
            CsvExporter.export_categories(
                categories, self.config.output_dir / "categories.csv", self.config
            )
        self._categories = categories
        return categories

    def _try_load_contents(
        self, count: int, csv_path: Optional[Union[str, Path]] = None
    ) -> Optional[List[Content]]:
        """Try to load contents from CSV file."""
        from logfaker.utils.csv import CsvExporter

        # Try output_dir first if no specific path provided
        if csv_path is None:
            file_path = CsvExporter._resolve_path("contents.csv", self.config)
        else:
            file_path = CsvExporter._resolve_path(csv_path, self.config)

        self.logger.debug(f"Looking for contents file at: {file_path}")
        if file_path.exists():
            contents = CsvImporter.import_content(file_path)
            if contents and len(contents) >= count:
                self.logger.info(f"Reusing {count} items from {file_path}")
                return contents[:count]
        return None

    def generate_contents(
        self,
        count: int,
        reuse_file: bool = True,
        csv_path: Optional[Union[str, Path]] = None,
    ) -> List[Content]:
        """
        Generate multiple content entries with category-based limits.

        Args:
            count: Number of contents to generate (max 1000)
            reuse_file: If True, try to load from contents.csv first
            csv_path: Optional path to contents.csv file. If not provided, uses output_dir/contents.csv or contents.csv

        Returns:
            List of Content objects

        Raises:
            ContentGenerationError: If count exceeds 1000
        """
        if count > 1000:
            raise ContentGenerationError("Cannot generate more than 1000 items")

        if reuse_file:
            contents = self._try_load_contents(count, csv_path)
            if contents:
                return contents

        self.logger.info(f"Starting content generation for {self.config.service_type}")
        categories = self._load_or_generate_categories()
        self.logger.info(f"Using {len(categories)} categories")
        for cat in categories:
            self.logger.debug(f"Category: {cat.name} - {cat.description}")

        contents = []
        for i in range(count):
            category = categories[i % len(categories)]
            content = self._generate_content_for_category(
                category=category, content_id=i + 1
            )
            contents.append(content)
            self.logger.info(f"Progress: {len(contents)}/{count} items generated")

        self.logger.info("Content generation completed")
        return contents
