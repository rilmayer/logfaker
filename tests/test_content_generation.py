"""Tests for content generation functionality."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from logfaker.core.config import GeneratorConfig
from logfaker.core.exceptions import ContentGenerationError
from logfaker.generators.content import ContentGenerator

@pytest.fixture(autouse=True)
def cleanup_categories():
    """Clean up categories.csv before and after each test."""
    # Clean up before test
    categories_csv = Path("categories.csv")
    if categories_csv.exists():
        categories_csv.unlink()

    yield

    # Clean up after test
    if categories_csv.exists():
        categories_csv.unlink()


def test_category_generation(mock_openai_client, tmp_path):
    """Test that category generation produces expected number of categories."""
    config = GeneratorConfig(
        api_key="test-key",
        service_type="図書館の蔵書検索サービス",
        language="ja",
        output_dir=tmp_path
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


def test_content_generation_limits(mock_openai_client, tmp_path):
    """Test that content generation respects the 1000 item limit."""
    config = GeneratorConfig(
        api_key="test-key",
        service_type="図書館の蔵書検索サービス",
        language="ja",
        output_dir=tmp_path
    )
    generator = ContentGenerator(config)
    generator.client = mock_openai_client

    # Should raise error for more than 1000 items
    with pytest.raises(ContentGenerationError):
        generator.generate_contents(1001)

    # Should work for exactly 50 items
    contents = generator.generate_contents(50)
    assert len(contents) == 50


def test_content_generation_output(mock_openai_client, tmp_path):
    """Test that generated content has all required fields."""
    config = GeneratorConfig(
        api_key="test-key",
        service_type="図書館の蔵書検索サービス",
        language="ja",
        output_dir=tmp_path
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


def test_category_persistence(tmp_path, mock_openai_client):
    """Test that categories are properly persisted and reused."""
    config = GeneratorConfig(
        api_key="test-key",
        output_dir=tmp_path
    )
    generator = ContentGenerator(config)
    generator.client = mock_openai_client

    # Generate initial categories
    contents = generator.generate_contents(10)
    assert (tmp_path / "categories.csv").exists()

    # Create new generator and verify categories are reused
    generator2 = ContentGenerator(config)
    generator2.client = mock_openai_client
    contents2 = generator2.generate_contents(10)

    # Categories should match
    assert contents[0].category == contents2[0].category


def test_category_regeneration(tmp_path, mock_openai_client):
    """Test that categories are regenerated when count is insufficient."""
    config = GeneratorConfig(
        api_key="test-key",
        output_dir=tmp_path
    )
    generator = ContentGenerator(config)
    generator.client = mock_openai_client

    # Generate initial small set
    contents = generator.generate_contents(5)

    # Generate larger set - should trigger regeneration
    contents2 = generator.generate_contents(150)
    assert len(set(c.category for c in contents2)) >= 100


def test_category_cycling(tmp_path, mock_openai_client):
    """Test that categories are cycled through when generating content."""
    config = GeneratorConfig(
        api_key="test-key",
        output_dir=tmp_path
    )

    generator = ContentGenerator(config)
    generator.client = mock_openai_client

    # Generate content with more items than categories
    contents = generator.generate_contents(20)
    categories = set(c.category for c in contents)

    # Verify that categories are reused in a cyclic manner
    for i, content in enumerate(contents):
        expected_category = contents[i % len(categories)].category
        assert content.category == expected_category
