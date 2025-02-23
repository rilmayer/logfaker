"""Content generation using AI."""
from typing import List, Optional

from openai import OpenAI

from logfaker.core.config import GeneratorConfig
from logfaker.core.models import BookContent


class ContentGenerator:
    """Generates realistic book content using AI."""

    def __init__(self, config: GeneratorConfig):
        """Initialize the content generator."""
        self.config = config
        self.client = OpenAI(api_key=config.api_key)

    def generate_book(self, category: Optional[str] = None) -> BookContent:
        """
        Generate a single book entry.

        Args:
            category: Optional category for the book

        Returns:
            BookContent object with generated data
        """
        # Implementation will use OpenAI to generate realistic book data
        prompt = self._create_book_prompt(category)
        response = self.client.chat.completions.create(
            model=self.config.ai_model,
            messages=[
                {"role": "system", "content": "You are a library catalog assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse the response and create a BookContent object
        # This is a placeholder implementation
        return BookContent(
            content_id=1,  # Will be replaced with actual ID generation
            title="Sample Book",
            description="Sample Description",
            category=category or "General",
        )

    def generate_books(
        self,
        count: int,
        categories: Optional[List[str]] = None
    ) -> List[BookContent]:
        """
        Generate multiple book entries.

        Args:
            count: Number of books to generate
            categories: Optional list of categories to use

        Returns:
            List of BookContent objects
        """
        return [self.generate_book(category=categories[i % len(categories)] if categories else None)
                for i in range(count)]

    def _create_book_prompt(self, category: Optional[str]) -> str:
        """Create a prompt for book generation."""
        base_prompt = "Generate a realistic book entry with title, description, "
        if category:
            base_prompt += f"in the category: {category}, "
        base_prompt += "author, publisher, year, and genre."
        return base_prompt
