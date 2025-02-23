"""Tests for CSV file reuse functionality."""

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from logfaker.core.config import GeneratorConfig
from logfaker.core.models import Category
from logfaker.generators.content import ContentGenerator
from logfaker.core.config import LogfakerConfig
from logfaker.generators.users import UserGenerator
from logfaker.utils.csv import CsvExporter


def test_content_file_reuse(mock_openai_client, tmp_path):
    """Test that content generation reuses CSV files."""
    config = GeneratorConfig(
        api_key="test-key",
        service_type="図書館の蔵書検索サービス",
        language="ja"
    )
    generator = ContentGenerator(config)
    
    # Configure mock response
    mock_response = MagicMock()
    mock_response.choices[0].message.function_call.arguments = json.dumps({
        "title": "人工知能入門",
        "description": "AIの基礎から応用まで網羅的に解説するガイド"
    })
    mock_openai_client.chat.completions.create.return_value = mock_response
    generator.client = mock_openai_client
    
    # Generate and save content
    contents = generator.generate_contents(10, reuse_file=False)
    csv_path = tmp_path / "contents.csv"
    CsvExporter.export_content(contents, csv_path)
    
    # Try to generate again with reuse
    reused = generator.generate_contents(10, reuse_file=True)
    assert len(reused) == len(contents)
    assert all(r.content_id == c.content_id for r, c in zip(reused, contents))


def test_user_file_reuse(mock_openai_client, tmp_path, monkeypatch):
    """Test that user generation reuses CSV files."""
    config = GeneratorConfig(
        api_key="test-key",
        service_type="図書館の蔵書検索サービス",
        language="ja"
    )
    generator = UserGenerator(config)
    
    # Configure mock responses for multiple users
    def create_mock_response(user_id):
        mock_response = MagicMock()
        mock_response.choices[0].message.function_call.arguments = json.dumps({
            "brief_explanation": f"技術書が好きなエンジニア {user_id}",
            "profession": "エンジニア",
            "preferences": ["テクノロジー", "文学"]
        })
        return mock_response
    
    mock_openai_client.chat.completions.create.side_effect = [
        create_mock_response(i) for i in range(1, 6)
    ]
    generator.client = mock_openai_client
    
    # Create test categories
    categories = [
        Category(name="テクノロジー", description="技術関連の書籍"),
        Category(name="文学", description="小説や詩集")
    ]
    
    # Generate and save users
    users = generator.generate_users(5, categories, reuse_file=False)
    csv_path = tmp_path / "users.csv"
    CsvExporter.export_users(users, csv_path)
    
    # Patch the file path for reuse test
    monkeypatch.chdir(tmp_path)
    
    # Reset mock and try to generate again with reuse
    mock_openai_client.reset_mock()
    reused = generator.generate_users(5, categories, reuse_file=True)
    assert len(reused) == len(users)
    assert all(r.user_id == u.user_id for r, u in zip(reused, users))
    assert all(r.preferences == u.preferences for r, u in zip(reused, users))

def test_output_directory_config(tmp_path):
    """Test that output directory configuration works."""
    output_dir = tmp_path / "outputs"
    config = LogfakerConfig(output_dir=output_dir)
    
    # Test with filename only
    CsvExporter.export_users([], "users.csv", config=config)
    assert (output_dir / "users.csv").exists()
    
    # Test with absolute path (should ignore output_dir)
    abs_path = tmp_path / "elsewhere" / "users.csv"
    CsvExporter.export_users([], abs_path, config=config)
    assert abs_path.exists()
    
    # Test with relative path containing directories
    rel_path = Path("subdir/users.csv")
    CsvExporter.export_users([], rel_path, config=config)
    assert (Path.cwd() / rel_path).exists()
