"""Tests for content generation functionality."""

from unittest.mock import MagicMock, patch

import pytest

from logfaker.core.config import GeneratorConfig
from logfaker.core.exceptions import ContentGenerationError
from logfaker.generators.content import ContentGenerator


def test_category_generation(mock_openai_client):
    """Test that category generation produces expected number of categories."""
    config = GeneratorConfig(
        api_key="test-key",
        service_type="図書館の蔵書検索サービス",
        language="ja"
    )
    generator = ContentGenerator(config)
    generator.client = mock_openai_client
    
    categories = generator._generate_categories()
    
    # Verify OpenAI was called correctly
    mock_openai_client.chat.completions.create.assert_called_once()
    
    # Categories should have required fields
    for category in categories:
        assert category.name
        assert category.description


def test_content_generation_limits(mock_openai_client):
    """Test that content generation respects the 1000 item limit."""
    config = GeneratorConfig(
        api_key="test-key",
        service_type="図書館の蔵書検索サービス",
        language="ja"
    )
    generator = ContentGenerator(config)
    generator.client = mock_openai_client
    
    # Should raise error for more than 1000 items
    with pytest.raises(ContentGenerationError):
        generator.generate_contents(1001)
    
    # Should work for exactly 50 items
    contents = generator.generate_contents(50)
    assert len(contents) == 50


def test_content_generation_output(mock_openai_client):
    """Test that generated content has all required fields."""
    config = GeneratorConfig(
        api_key="test-key",
        service_type="図書館の蔵書検索サービス",
        language="ja"
    )
    generator = ContentGenerator(config)
    generator.client = mock_openai_client
    
    # Generate a small set of content
    contents = generator.generate_contents(10)
    assert len(contents) == 10
    
    # Verify content structure
    for content in contents:
        assert content.content_id > 0
        assert content.title
        assert content.description
        assert content.category
