"""Integration tests for user generation with OpenAI API."""

import json
import os
from unittest.mock import MagicMock

import pytest

from logfaker.core.config import GeneratorConfig
from logfaker.core.models import UserProfile
from logfaker.generators.users import UserGenerator
from logfaker.utils.csv import CsvExporter


def test_openai_user_generation(mock_openai_client):
    """Test user generation with mock OpenAI."""
    config = GeneratorConfig(
        api_key="test-key", service_type="図書館の蔵書検索サービス", language="ja"
    )

    # Configure mock responses
    def create_category_response():
        mock_response = MagicMock()
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.function_call = MagicMock()
        mock_response.choices[0].message.function_call.name = "create_categories"
        mock_response.choices[0].message.function_call.arguments = json.dumps(
            {
                "categories": [
                    {"name": f"カテゴリー{i}", "description": f"説明{i}"}
                    for i in range(1, 101)
                ]
            }
        )
        return mock_response

    def create_user_response():
        mock_response = MagicMock()
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.function_call = MagicMock()
        mock_response.choices[0].message.function_call.name = "create_user"
        mock_response.choices[0].message.function_call.arguments = json.dumps(
            {
                "brief_explanation": "技術書が好きなエンジニア",
                "profession": "エンジニア",
                "preferences": ["カテゴリー1", "カテゴリー2"],
            }
        )
        return mock_response

    mock_openai_client.chat.completions.create.side_effect = [
        create_category_response(),  # First call for categories
        create_user_response(),  # Then user response
    ]

    generator = UserGenerator(config)
    generator.client = mock_openai_client
    generator.content_generator.client = mock_openai_client
    user = generator.generate_user()

    # Verify user profile structure and content
    assert user.user_id > 0, "User ID should be positive"
    assert user.brief_explanation, "Brief explanation should not be empty"
    assert user.profession, "Profession should not be empty"
    assert user.preferences, "Preferences should not be empty"
    # Get category names from the mock response
    categories = json.loads(
        create_category_response().choices[0].message.function_call.arguments
    )["categories"]
    category_names = [cat["name"] for cat in categories]
    assert all(
        pref in category_names for pref in user.preferences
    ), "All preferences should be from provided categories"


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not set")
def test_openai_multiple_user_generation():
    """Test generating multiple users with real OpenAI API."""
    config = GeneratorConfig(
        api_key=os.getenv("OPENAI_API_KEY"),
        service_type="図書館の蔵書検索サービス",
        language="ja",
        ai_model="gpt-3.5-turbo",  # Using a stable model for testing
    )

    generator = UserGenerator(config)
    users = generator.generate_users(count=3)

    assert len(users) == 3, "Should generate requested number of users"
    for i, user in enumerate(users, 1):
        assert user.user_id == i, f"User ID should be {i}"
        assert user.preferences, "Each user should have preferences"
        assert all(
            pref.startswith("カテゴリー") for pref in user.preferences
        ), f"All preferences for user {i} should be from generated categories"


def test_user_generation_file_reuse(tmp_path, mock_openai_client):
    """Test file reuse functionality and preference validation."""
    config = GeneratorConfig(
        api_key="test-key", service_type="図書館の蔵書検索サービス", language="ja"
    )

    # Configure mock responses
    def create_category_response():
        mock_response = MagicMock()
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.function_call = MagicMock()
        mock_response.choices[0].message.function_call.name = "create_categories"
        mock_response.choices[0].message.function_call.arguments = json.dumps(
            {
                "categories": [
                    {"name": f"カテゴリー{i}", "description": f"説明{i}"}
                    for i in range(1, 101)
                ]
            }
        )
        return mock_response

    def create_user_response():
        mock_response = MagicMock()
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.function_call = MagicMock()
        mock_response.choices[0].message.function_call.name = "create_user"
        mock_response.choices[0].message.function_call.arguments = json.dumps(
            {
                "brief_explanation": "技術書が好きなエンジニア",
                "profession": "エンジニア",
                "preferences": ["カテゴリー1"],
            }
        )
        return mock_response

    mock_openai_client.chat.completions.create.side_effect = [
        create_category_response(),  # First call for categories
        create_user_response(),  # Then user response
    ]

    generator = UserGenerator(config)
    generator.client = mock_openai_client
    generator.content_generator.client = mock_openai_client

    # Create test users directly
    original_users = [
        UserProfile(
            user_id=1,
            brief_explanation="技術書が好きなエンジニア",
            profession="エンジニア",
            preferences=["カテゴリー1"],
        ),
        UserProfile(
            user_id=2,
            brief_explanation="小説が好きな学生",
            profession="学生",
            preferences=["カテゴリー2"],
        ),
    ]
    csv_path = tmp_path / "users.csv"
    CsvExporter.export_users(original_users, csv_path)

    # Try to generate again with reuse using absolute path
    reused_users = generator.generate_users(count=2, reuse_file=True, csv_path=csv_path)
    assert len(reused_users) == len(original_users), "Should reuse same number of users"
    for orig, reused in zip(original_users, reused_users):
        assert orig.user_id == reused.user_id, "User IDs should match"
        assert orig.preferences == reused.preferences, "Preferences should match"


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not set")
def test_openai_user_generation_error_handling():
    """Test error handling with invalid API key."""
    config = GeneratorConfig(
        api_key=os.getenv("OPENAI_API_KEY"),
        service_type="図書館の蔵書検索サービス",
        language="ja",
    )

    generator = UserGenerator(config)
    with pytest.raises(Exception):  # Should raise an OpenAI API error
        generator.generate_user()


# OpenAI APIを使用してテストする場合は以下のコメントを外して実行
# if __name__ == "__main__":
#     import os
#     import logging
#     logging.basicConfig(level=logging.INFO)
#     config = GeneratorConfig(
#         api_key=os.getenv("OPENAI_API_KEY"),
#         service_type="図書館の蔵書検索サービス",
#         language="ja"
#     )
#     generator = UserGenerator(config)
#     categories = [
#         Category(id=1, name="テクノロジー", description="技術関連の書籍"),
#         Category(id=2, name="文学", description="小説や詩集"),
#         Category(id=3, name="ビジネス", description="ビジネスと経営の書籍")
#     ]
#     users = generator.generate_users(count=3, reuse_file=False)
#     for user in users:
#         print(user.user_id)
#         print(user.brief_explanation)
#         print(user.profession)
#         print(user.preferences)
