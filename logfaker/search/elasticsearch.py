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
        auth = None
        if config.username and config.password:
            auth = (config.username, config.password)
        self.client = Elasticsearch(
            f"http://{config.host}:{config.port}", basic_auth=auth
        )

    def search(
        self, query: str, max_results: int = 10, category: Optional[str] = None
    ) -> List[SearchResult]:
        """Execute search query against Elasticsearch."""
        try:
            analyzer = (
                "kuromoji_analyzer" if self.config.language == "ja" else "standard"
            )
            # Build search query
            search_body = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["title", "description", "abstract"],
                                    "analyzer": analyzer,
                                }
                            }
                        ]
                    }
                },
                "size": max_results,
            }

            if category:
                search_body["query"]["bool"]["filter"] = [
                    {"term": {"category": category}}
                ]

            # Execute search
            # Elasticsearch response typing
            response = self.client.search(
                index=self.config.index, body=search_body  # type: ignore[index]
            )
            hits_container = response.get("hits", {})  # type: ignore[union-attr]
            hits = hits_container.get("hits", [])

            # Convert results
            return [
                SearchResult(
                    content_id=int(hit.get("_id", 0)),
                    title=hit.get("_source", {}).get("title", ""),
                    relevance_score=float(hit.get("_score", 0.0)),
                )
                for hit in hits
            ]

        except Exception as e:
            raise SearchEngineError(f"Search failed: {str(e)}")

    def index_content(self, content_id: int, data: dict) -> bool:
        """Index new content in Elasticsearch."""
        try:
            response = self.client.index(
                index=self.config.index, id=str(content_id), document=data
            )
            return response["result"] in ["created", "updated"]
        except Exception as e:
            raise SearchEngineError(f"Indexing failed: {str(e)}")

    def setup_index(self, force: bool = False) -> bool:
        """Set up the search index, optionally forcing recreation.

        Args:
            force: If True, delete existing index before setup

        Returns:
            True if setup was successful
        """
        try:
            if force and self.client.indices.exists(index=self.config.index):
                self.delete_index()

            if not self.client.indices.exists(index=self.config.index):
                if self.config.language == "ja":
                    index_body = {
                        "settings": {
                            "analysis": {
                                "tokenizer": {
                                    "kuromoji_search_tokenizer": {
                                        "type": "kuromoji_tokenizer",
                                        "mode": "search",
                                    }
                                },
                                "analyzer": {
                                    "kuromoji_analyzer": {
                                        "type": "custom",
                                        "tokenizer": "kuromoji_search_tokenizer",
                                        "filter": [
                                            "kuromoji_baseform",
                                            "kuromoji_part_of_speech",
                                            "ja_stop",
                                        ],
                                    }
                                },
                            }
                        },
                        "mappings": {
                            "properties": {
                                "title": {
                                    "type": "text",
                                    "analyzer": "kuromoji_analyzer",
                                },
                                "description": {
                                    "type": "text",
                                    "analyzer": "kuromoji_analyzer",
                                },
                                "abstract": {
                                    "type": "text",
                                    "analyzer": "kuromoji_analyzer",
                                },
                                "category": {"type": "keyword"},
                            }
                        },
                    }
                else:
                    index_body = {}  # デフォルトの設定を使用

                self.client.indices.create(index=self.config.index, body=index_body)
            return True
        except Exception as e:
            raise SearchEngineError(f"Index setup failed: {str(e)}")

    def delete_index(self) -> bool:
        """Delete the current index if it exists."""
        try:
            if self.client.indices.exists(index=self.config.index):
                response = self.client.indices.delete(index=self.config.index)
                return response["acknowledged"]
            return True
        except Exception as e:
            raise SearchEngineError(f"Failed to delete index: {str(e)}")

    def is_healthy(self) -> bool:
        """Check Elasticsearch cluster health."""
        try:
            health = self.client.cluster.health()
            return health["status"] in ["green", "yellow"]
        except Exception:
            return False
