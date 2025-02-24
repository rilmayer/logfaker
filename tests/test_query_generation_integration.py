"""Integration tests for query generation with OpenAI API."""

import os
import pytest
from logfaker.core.config import GeneratorConfig
from logfaker.core.models import UserProfile
from logfaker.generators.queries import QueryGenerator

@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not set")
def test_openai_query_generation():
    """Test query generation with real OpenAI API."""
    config = GeneratorConfig(
        api_key=os.getenv("OPENAI_API_KEY"),
        service_type="図書館の蔵書検索サービス",
        language="ja",
        ai_model="gpt-3.5-turbo"  # Using a stable model for testing
    )

    generator = QueryGenerator(config)
    user = UserProfile(
        user_id=1,
        brief_explanation="技術書が好きなエンジニア",
        profession="エンジニア",
        preferences=["プログラミング", "AI"]
    )

    query = generator.generate_query(user)

    # Verify query structure and content
    assert query.query_content, "Query content should not be empty"
    assert query.category, "Query category should not be empty"
    assert query.user_id == user.user_id, "Query should be associated with the user"
    assert isinstance(query.query_content, str), "Query content should be a string"
    assert isinstance(query.category, str), "Query category should be a string"


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not set")
def test_openai_query_generation_error_handling():
    """Test error handling with invalid API key."""
    config = GeneratorConfig(
        api_key="invalid-key",
        service_type="図書館の蔵書検索サービス",
        language="ja"
    )

    generator = QueryGenerator(config)
    user = UserProfile(
        user_id=1,
        brief_explanation="技術書が好きなエンジニア",
        profession="エンジニア",
        preferences=["プログラミング", "AI"]
    )

    with pytest.raises(Exception):  # Should raise an OpenAI API error
        generator.generate_query(user)
