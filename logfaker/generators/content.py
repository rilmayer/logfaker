"""Content generation using AI."""

from typing import List, Optional

from openai import OpenAI

from logfaker.core.config import GeneratorConfig
from logfaker.core.models import Content


class ContentGenerator:
    """Generates content using AI."""

    def __init__(self, config: GeneratorConfig):
        """Initialize the content generator."""
        self.config = config
        self.client = OpenAI(api_key=config.api_key)

    def generate_content(self, category: Optional[str] = None) -> Content:
        """
        Generate a single content entry.

        Args:
            category: Optional category for the content

        Returns:
            Content object with generated data
        """
        prompt = self._create_content_prompt(category)
        response = self.client.chat.completions.create(
            model=self.config.ai_model,
            messages=[
                {"role": "system", "content": "You are a content generator."},
                {"role": "user", "content": prompt},
            ],
        )

        return Content(
            content_id=1,  # Will be replaced with actual ID generation
            title="Sample Content",
            description="Sample Description",
            category=category or "General",
        )

    def generate_contents(
        self, count: int, categories: Optional[List[str]] = None
    ) -> List[Content]:
        """
        Generate multiple content entries.

        Args:
            count: Number of contents to generate
            categories: Optional list of categories to use

        Returns:
            List of Content objects
        """
        return [
            self.generate_content(
                category=categories[i % len(categories)] if categories else None
            )
            for i in range(count)
        ]

    def _create_content_prompt(self, category: Optional[str]) -> str:
        """Create a prompt for content generation."""
        base_prompt = "Generate a simple content entry with title and description "
        if category:
            base_prompt += f"in the category: {category}"
        return base_prompt
