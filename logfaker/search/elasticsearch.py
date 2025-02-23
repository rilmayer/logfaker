"""Elasticsearch implementation of search engine interface."""
from typing import List, Optional

from elasticsearch import Elasticsearch

from logfaker.core.config import SearchEngineConfig
from logfaker.core.exceptions import SearchEngineError
from logfaker.core.models import SearchResult
from logfaker.search.base import SearchEngine


class ElasticsearchEngine(SearchEngine):
    """Elasticsearch-based search implementation."""

    def __init__(self, config: SearchEngineConfig):
        """Initialize Elasticsearch connection."""
        self.config = config
        self.client = Elasticsearch(
            f"http://{config.host}:{config.port}",
            basic_auth=(config.username, config.password) if config.username else None
        )

    def search(
        self,
        query: str,
        max_results: int = 10,
        category: Optional[str] = None
    ) -> List[SearchResult]:
        """Execute search query against Elasticsearch."""
        try:
            # Build search query
            search_body = {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"_all": query}}
                        ]
                    }
                },
                "size": max_results
            }

            if category:
                search_body["query"]["bool"]["filter"] = [
                    {"term": {"category": category}}
                ]

            # Execute search
            response = self.client.search(
                index=self.config.index,
                body=search_body
            )

            # Convert results
            return [
                SearchResult(
                    content_id=hit["_id"],
                    title=hit["_source"]["title"],
                    url=f"https://library.example.com/book/{hit['_id']}",
                    relevance_score=hit["_score"]
                )
                for hit in response["hits"]["hits"]
            ]

        except Exception as e:
            raise SearchEngineError(f"Search failed: {str(e)}")

    def index_content(self, content_id: int, data: dict) -> bool:
        """Index new content in Elasticsearch."""
        try:
            response = self.client.index(
                index=self.config.index,
                id=str(content_id),
                document=data
            )
            return response["result"] in ["created", "updated"]
        except Exception as e:
            raise SearchEngineError(f"Indexing failed: {str(e)}")

    def is_healthy(self) -> bool:
        """Check Elasticsearch cluster health."""
        try:
            health = self.client.cluster.health()
            return health["status"] in ["green", "yellow"]
        except Exception:
            return False
