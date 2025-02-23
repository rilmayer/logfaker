"""Tests for query generation functionality."""

from unittest.mock import MagicMock, patch
import pytest

from logfaker.core.config import GeneratorConfig
from logfaker.core.models import UserProfile
from logfaker.generators.queries import QueryGenerator


def test_query_generation(mock_openai_client):
    """Test that query generation produces valid queries."""
    config = GeneratorConfig(
        api_key="test-key",
        service_type="図書館の蔵書検索サービス",
        language="ja"
    )
    generator = QueryGenerator(config)
    generator.client = mock_openai_client
    
    user = UserProfile(
        user_id=1,
        brief_explanation="技術書が好きなエンジニア",
        profession="エンジニア",
        preferences=["プログラミング", "AI"]
    )
    
    query = generator.generate_query(user)
    assert query.query_content
    assert query.category
    assert query.user_id == user.user_id


def test_multiple_query_generation(mock_openai_client):
    """Test that multiple query generation works correctly."""
    config = GeneratorConfig(
        api_key="test-key",
        service_type="図書館の蔵書検索サービス",
        language="ja"
    )
    generator = QueryGenerator(config)
    generator.client = mock_openai_client
    
    user = UserProfile(
        user_id=1,
        brief_explanation="技術書が好きなエンジニア",
        profession="エンジニア",
        preferences=["プログラミング", "AI"]
    )
    
    queries = generator.generate_queries(user, count=3)
    assert len(queries) == 3
    for i, query in enumerate(queries, 1):
        assert query.query_id == i
        assert query.user_id == user.user_id
        assert query.query_content
        assert query.category
