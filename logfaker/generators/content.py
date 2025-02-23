"""Content generation using AI."""

import json
import logging
from pathlib import Path
from typing import List, Optional

from openai import OpenAI

from logfaker.core.config import GeneratorConfig
from logfaker.core.exceptions import ContentGenerationError
from logfaker.core.models import Category, Content
from logfaker.utils.importer import CsvImporter


class ContentGenerator:
    """Generates content using AI."""

    def __init__(self, config: GeneratorConfig):
        """Initialize the content generator."""
        self.config = config
        self.client = OpenAI(api_key=config.api_key)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, config.log_level))

    def _generate_categories(self) -> List[Category]:
        """
        Generate categories using function calling.

        Returns:
            List of Category objects
        """
        functions = [{
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
                                "description": {"type": "string"}
                            },
                            "required": ["name", "description"]
                        }
                    }
                },
                "required": ["categories"]
            }
        }]
        
        response = self.client.chat.completions.create(
            model=self.config.ai_model,
            messages=[{
                "role": "system",
                "content": f"Generate approximately 100 categories for {self.config.service_type} in {self.config.language}. Categories should be diverse and cover all potential content types."
            }],
            functions=functions,
            function_call={"name": "create_categories"}
        )
        
        result = json.loads(response.choices[0].message.function_call.arguments)
        return [Category(**cat) for cat in result["categories"]]

    def _generate_content_for_category(self, category: Category, content_id: int) -> Content:
        """
        Generate a single content entry using function calling.

        Args:
            category: Category to generate content for
            content_id: Unique identifier for the content

        Returns:
            Content object with generated data
        """
        functions = [{
            "name": "create_content",
            "description": "Create content item",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["title", "description"]
            }
        }]

        response = self.client.chat.completions.create(
            model=self.config.ai_model,
            messages=[{
                "role": "system",
                "content": f"Generate content for category '{category.name}' ({category.description}) in {self.config.service_type}. Use {self.config.language} language. Be care about the generated content is not overlapped with the actual content in the real world."
            }],
            functions=functions,
            function_call={"name": "create_content"}
        )

        result = json.loads(response.choices[0].message.function_call.arguments)
        return Content(
            content_id=content_id,
            title=result["title"],
            description=result["description"],
            category=category.name
        )

    def generate_contents(self, count: int, reuse_file: bool = True) -> List[Content]:
        """
        Generate multiple content entries with category-based limits.

        Args:
            count: Number of contents to generate (max 1000)
            reuse_file: If True, try to load from contents.csv first

        Returns:
            List of Content objects

        Raises:
            ContentGenerationError: If count exceeds 1000
        """
        if count > 1000:
            raise ContentGenerationError("Cannot generate more than 1000 items")
            
        if reuse_file:
            contents = CsvImporter.import_content("contents.csv")
            if contents and len(contents) >= count:
                self.logger.info(f"Reusing {count} items from contents.csv")
                return contents[:count]

        self.logger.info(f"Starting content generation for {self.config.service_type}")
        categories = self._generate_categories()
        self.logger.info(f"Generated {len(categories)} categories")
        for cat in categories:
            self.logger.debug(f"Category: {cat.name} - {cat.description}")

        # Generate only as many categories as needed
        categories = categories[:count]
        self.logger.info(f"Using {len(categories)} categories")
        
        contents = []
        for i in range(count):
            category = categories[i % len(categories)]
            content = self._generate_content_for_category(
                category=category,
                content_id=i + 1
            )
            contents.append(content)
            self.logger.info(f"Progress: {len(contents)}/{count} items generated")
        
        self.logger.info("Content generation completed")
        return contents
