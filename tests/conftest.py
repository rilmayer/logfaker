"""Test configuration for Logfaker."""

import json
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    def create_response(function_name):
        if function_name == "create_categories":
            # Generate 100+ categories for testing
            categories = []
            prefixes = ["技術", "文学", "科学", "芸術", "歴史", "社会", "自然", "文化", "経済", "教育"]
            suffixes = ["入門", "理論", "実践", "研究", "概論", "応用", "基礎", "発展", "解説", "分析"]
            descriptions = ["基本から応用まで", "詳細な解説", "実践的なガイド", "包括的な入門書", "専門的な解説"]

            for i, prefix in enumerate(prefixes):
                for j, suffix in enumerate(suffixes):
                    categories.append({
                        "name": f"{prefix}の{suffix}",
                        "description": f"{prefix}に関する{descriptions[j % len(descriptions)]}"
                    })

            arguments = {
                "categories": categories
            }
        elif function_name == "create_content":
            arguments = {
                "title": "人工知能入門",
                "description": "AIの基礎から応用まで網羅的に解説するガイド"
            }
        else:  # create_query
            arguments = {
                "query_content": "人工知能の基礎",
                "category": "テクノロジー"
            }

        return MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        function_call=MagicMock(
                            arguments=json.dumps(arguments)
                        )
                    )
                )
            ]
        )
    return create_response


@pytest.fixture
def mock_openai_client(monkeypatch, mock_openai_response):
    """Mock OpenAI client."""
    mock_client = MagicMock()
    def create_completion(**kwargs):
        function_name = kwargs.get("function_call", {}).get("name", "create_categories")
        return mock_openai_response(function_name)

    mock_client.chat.completions.create.side_effect = create_completion
    return mock_client
