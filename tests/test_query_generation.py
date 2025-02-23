"""Tests for query generation functionality."""

from unittest.mock import MagicMock, patch
import pytest

from logfaker.core.config import GeneratorConfig
from logfaker.core.models import SearchResult, UserProfile
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


def test_engagement_simulation():
    """Test that engagement simulation is deterministic."""
    config = GeneratorConfig(api_key="test-key")
    generator = QueryGenerator(config)
    
    user = UserProfile(
        user_id=1,
        brief_explanation="技術書が好きなエンジニア",
        profession="エンジニア",
        preferences=["プログラミング"]
    )
    
    results = [
        SearchResult(content_id=1, title="Test 1", url="http://test1"),
        SearchResult(content_id=2, title="Test 2", url="http://test2"),
        SearchResult(content_id=3, title="Test 3", url="http://test3"),
    ]
    
    # Same user should get same engagement metrics
    clicks1, ctr1 = generator.simulate_engagement(user, results)
    clicks2, ctr2 = generator.simulate_engagement(user, results)
    assert clicks1 == clicks2
    assert ctr1 == ctr2
    
    # Verify clicks and CTR are within bounds
    assert 0 <= clicks1 <= min(5, len(results))
    assert 0.0 <= ctr1 <= 1.0


def test_engagement_simulation_different_users():
    """Test that engagement simulation differs between users."""
    config = GeneratorConfig(api_key="test-key")
    generator = QueryGenerator(config)
    
    user1 = UserProfile(
        user_id=1,
        brief_explanation="技術書が好きなエンジニア",
        profession="エンジニア",
        preferences=["プログラミング"]
    )
    
    user2 = UserProfile(
        user_id=2,
        brief_explanation="文学が好きな学生",
        profession="学生",
        preferences=["文学"]
    )
    
    results = [
        SearchResult(content_id=1, title="Test 1", url="http://test1"),
        SearchResult(content_id=2, title="Test 2", url="http://test2"),
    ]
    
    # Different users should get different engagement metrics
    clicks1, ctr1 = generator.simulate_engagement(user1, results)
    clicks2, ctr2 = generator.simulate_engagement(user2, results)
    assert (clicks1, ctr1) != (clicks2, ctr2)
