"""Integration tests for user generation with OpenAI API."""

import os
import pytest
from logfaker.core.config import GeneratorConfig
from logfaker.core.models import Category, UserProfile
from logfaker.generators.users import UserGenerator
from logfaker.utils.csv import CsvExporter

@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not set")
def test_openai_user_generation():
    """Test user generation with real OpenAI API."""
    config = GeneratorConfig(
        api_key=os.getenv("OPENAI_API_KEY"),
        service_type="図書館の蔵書検索サービス",
        language="ja",
        ai_model="gpt-3.5-turbo"  # Using a stable model for testing
    )
    
    # Create test categories
    categories = [
        Category(id=1, name="テクノロジー", description="技術関連の書籍"),
        Category(id=2, name="文学", description="小説や詩集"),
        Category(id=3, name="ビジネス", description="ビジネスと経営の書籍")
    ]
    
    generator = UserGenerator(config)
    user = generator.generate_user(categories)
    
    # Verify user profile structure and content
    assert user.user_id > 0, "User ID should be positive"
    assert user.brief_explanation, "Brief explanation should not be empty"
    assert user.profession, "Profession should not be empty"
    assert user.preferences, "Preferences should not be empty"
    assert all(pref in [cat.name for cat in categories] for pref in user.preferences), \
        "All preferences should be from provided categories"


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not set")
def test_openai_multiple_user_generation():
    """Test generating multiple users with real OpenAI API."""
    config = GeneratorConfig(
        api_key=os.getenv("OPENAI_API_KEY"),
        service_type="図書館の蔵書検索サービス",
        language="ja",
        ai_model="gpt-3.5-turbo"  # Using a stable model for testing
    )
    
    categories = [
        Category(id=1, name="テクノロジー", description="技術関連の書籍"),
        Category(id=2, name="文学", description="小説や詩集")
    ]
    
    generator = UserGenerator(config)
    users = generator.generate_users(count=3, categories=categories)
    
    assert len(users) == 3, "Should generate requested number of users"
    for i, user in enumerate(users, 1):
        assert user.user_id == i, f"User ID should be {i}"
        assert user.preferences, "Each user should have preferences"
        assert all(pref in [cat.name for cat in categories] for pref in user.preferences), \
            f"All preferences for user {i} should be from provided categories"


def test_user_generation_file_reuse(tmp_path):
    """Test file reuse functionality and preference validation."""
    config = GeneratorConfig(
        api_key="dummy-key",
        service_type="図書館の蔵書検索サービス",
        language="ja"
    )
    
    categories = [
        Category(id=1, name="テクノロジー", description="技術関連の書籍"),
        Category(id=2, name="文学", description="小説や詩集")
    ]
    
    generator = UserGenerator(config)
    
    # Create test users directly
    original_users = [
        UserProfile(
            user_id=1,
            brief_explanation="技術書が好きなエンジニア",
            profession="エンジニア",
            preferences=["テクノロジー"]
        ),
        UserProfile(
            user_id=2,
            brief_explanation="小説が好きな学生",
            profession="学生",
            preferences=["文学"]
        )
    ]
    csv_path = tmp_path / "users.csv"
    CsvExporter.export_users(original_users, csv_path)
    
    # Try to generate again with reuse using absolute path
    reused_users = generator.generate_users(count=2, categories=categories, reuse_file=True, csv_path=csv_path)
    assert len(reused_users) == len(original_users), "Should reuse same number of users"
    for orig, reused in zip(original_users, reused_users):
        assert orig.user_id == reused.user_id, "User IDs should match"
        assert orig.preferences == reused.preferences, "Preferences should match"


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not set")
def test_openai_user_generation_error_handling():
    """Test error handling with invalid API key."""
    config = GeneratorConfig(
        api_key="invalid-key",
        service_type="図書館の蔵書検索サービス",
        language="ja"
    )
    
    categories = [
        Category(id=1, name="テクノロジー", description="技術関連の書籍")
    ]
    
    generator = UserGenerator(config)
    with pytest.raises(Exception):  # Should raise an OpenAI API error
        generator.generate_user(categories)

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
#     users = generator.generate_users(count=3, categories=categories, reuse_file=False)
#     for user in users:
#         print(user.user_id)
#         print(user.brief_explanation)
#         print(user.profession)
#         print(user.preferences)
