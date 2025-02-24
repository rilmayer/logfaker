"""Tests for CSV file reuse functionality."""

import json
import shutil
from pathlib import Path
from unittest.mock import MagicMock

import pytest

@pytest.fixture(autouse=True)
def cleanup_test_files(request, tmp_path):
    """Clean up test files after each test."""
    yield
    # Clean up tmp_path and any subdirectories
    if tmp_path.exists():
        shutil.rmtree(tmp_path)
    # Clean up any relative paths in current directory
    subdir = Path("subdir")
    if subdir.exists():
        shutil.rmtree(subdir)

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
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.function_call = MagicMock()
    mock_response.choices[0].message.function_call.name = "create_content"
    mock_response.choices[0].message.function_call.arguments = json.dumps({
        "title": "人工知能入門",
        "description": "AIの基礎から応用まで網羅的に解説するガイド",
        "category": "カテゴリー1"
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
    
    mock_openai_client.chat.completions.create.side_effect = [
        create_category_response(),  # First call for categories
        *[create_user_response(i + 1) for i in range(5)]  # Then user responses
    ]
    generator.client = mock_openai_client
    generator.content_generator.client = mock_openai_client
    
    # Create test categories
    categories = [
        Category(id=1, name="テクノロジー", description="技術関連の書籍"),
        Category(id=2, name="文学", description="小説や詩集")
    ]
    
    # Generate and save users
    users = generator.generate_users(5, reuse_file=False)
    csv_path = tmp_path / "users.csv"
    CsvExporter.export_users(users, csv_path)
    
    # Patch the file path for reuse test
    monkeypatch.chdir(tmp_path)
    
    # Reset mock and try to generate again with reuse
    mock_openai_client.reset_mock()
    reused = generator.generate_users(5, reuse_file=True)
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
    
    # Test assertions are done, cleanup will be handled by fixture


def create_category_response():
    """Create a mock response for category generation."""
    # Create the response data
    response_data = {
        "categories": [
            {"name": f"カテゴリー{i}", "description": f"説明{i}"}
            for i in range(1, 101)
        ]
    }
    
    # Create a proper mock structure
    mock = MagicMock()
    mock.choices = [MagicMock()]
    mock.choices[0].message = MagicMock()
    mock.choices[0].message.function_call = MagicMock()
    mock.choices[0].message.function_call.name = "create_categories"
    mock.choices[0].message.function_call.arguments = json.dumps(response_data)
    mock.choices[0].message.content = None
    mock.choices[0].finish_reason = "function_call"
    
    # Configure mock to return the same arguments string consistently
    mock.choices[0].message.function_call.configure_mock(arguments=json.dumps(response_data))
    
    # Add debug logging
    print(f"\nCategory response mock args:", mock.choices[0].message.function_call.arguments)
    print(f"Category response mock type:", type(mock.choices[0].message.function_call.arguments))
    return mock


def create_content_response():
    """Create a mock response for content generation."""
    # Create the response data
    response_data = {
        "title": "人工知能入門",
        "description": "AIの基礎から応用まで網羅的に解説するガイド",
        "category": "カテゴリー1"
    }
    
    # Create a proper mock structure
    mock = MagicMock()
    mock.choices = [MagicMock()]
    mock.choices[0].message = MagicMock()
    mock.choices[0].message.function_call = MagicMock()
    mock.choices[0].message.function_call.name = "create_content"
    mock.choices[0].message.function_call.arguments = json.dumps(response_data)
    mock.choices[0].message.content = None
    mock.choices[0].finish_reason = "function_call"
    
    # Configure mock to return the same arguments string consistently
    mock.choices[0].message.function_call.configure_mock(arguments=json.dumps(response_data))
    
    # Add debug logging
    print(f"\nContent response mock args:", mock.choices[0].message.function_call.arguments)
    print(f"Content response mock type:", type(mock.choices[0].message.function_call.arguments))
    return mock


def create_user_response(user_id: int):
    """Create a mock response for user generation."""
    # Create the response data with valid category names
    response_data = {
        "brief_explanation": f"技術書が好きなエンジニア {user_id}",
        "profession": "エンジニア",
        "preferences": [f"カテゴリー{i}" for i in range(1, 3)]  # Use first two categories
    }
    
    # Create a proper mock structure
    mock = MagicMock()
    mock.choices = [MagicMock()]
    mock.choices[0].message = MagicMock()
    mock.choices[0].message.function_call = MagicMock()
    mock.choices[0].message.function_call.name = "create_user"
    mock.choices[0].message.function_call.arguments = json.dumps(response_data)
    mock.choices[0].message.content = None
    mock.choices[0].finish_reason = "function_call"
    
    # Configure mock to return the same arguments string consistently
    mock.choices[0].message.function_call.configure_mock(arguments=json.dumps(response_data))
    
    # Add debug logging
    print(f"\nUser response {user_id} data:", response_data)
    print(f"User response {user_id} mock args:", mock.choices[0].message.function_call.arguments)
    print(f"User response {user_id} mock type:", type(mock.choices[0].message.function_call.arguments))
    return mock


def test_output_directory_reuse(mock_openai_client, tmp_path):
    """Test that generators reuse files from output directory."""
    output_dir = tmp_path / "outputs"
    output_dir.mkdir(parents=True)
    
    # Create configs for generators and exporter
    gen_config = GeneratorConfig(
        api_key="test-key",
        service_type="図書館の蔵書検索サービス",
        language="ja",
        output_dir=output_dir
    )
    export_config = LogfakerConfig(output_dir=output_dir)
    
    # Test content reuse from output directory
    content_gen = ContentGenerator(gen_config)
    
    # Set up mock responses for content generation
    mock_openai_client.chat.completions.create.side_effect = [
        create_category_response(),  # First call for categories
        *[create_content_response() for _ in range(10)]  # Then content responses
    ]
    content_gen.client = mock_openai_client
    
    contents = content_gen.generate_contents(10, reuse_file=False)
    CsvExporter.export_content(contents, "contents.csv", config=export_config)
    
    # Should find and reuse content from output directory
    reused = content_gen.generate_contents(10, reuse_file=True)
    assert len(reused) == len(contents)
    assert all(r.content_id == c.content_id for r, c in zip(reused, contents))
    
    # Test user reuse from output directory
    user_gen = UserGenerator(gen_config)
    
    # Create separate mock clients for user and content generation
    user_mock = MagicMock()
    content_mock = MagicMock()
    
    # Set up mock responses for user generation
    user_mock.chat.completions.create.side_effect = [create_user_response(i + 1) for i in range(5)]
    
    # Set up mock response for category generation
    content_mock.chat.completions.create.return_value = create_category_response()
    
    # Configure generators to use separate mocks
    user_gen.client = user_mock
    user_gen.content_generator.client = content_mock
    
    users = user_gen.generate_users(5, reuse_file=False)
    CsvExporter.export_users(users, "users.csv", config=export_config)
    
    # Should find and reuse users from output directory
    reused = user_gen.generate_users(5, reuse_file=True)
    assert len(reused) == len(users)
    assert all(r.user_id == u.user_id for r, u in zip(reused, users))
    assert all(r.preferences == u.preferences for r, u in zip(reused, users))
