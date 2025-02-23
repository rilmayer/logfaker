"""Test configuration for Logfaker."""

import json
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    def create_response(function_name):
        if function_name == "create_categories":
            arguments = {
                "categories": [
                    {"name": "テクノロジー", "description": "技術関連の書籍"},
                    {"name": "プログラミング", "description": "プログラミング関連の書籍"},
                    {"name": "データサイエンス", "description": "データ分析と機械学習の書籍"},
                    {"name": "ビジネス", "description": "ビジネスと経営の書籍"},
                    {"name": "文学", "description": "小説と文学作品"},
                    {"name": "歴史", "description": "歴史関連の書籍"}
                ]
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
