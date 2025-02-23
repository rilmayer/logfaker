"""Configuration settings for Logfaker."""

from typing import Dict, Optional

from pydantic import BaseModel, Field


class SearchEngineConfig(BaseModel):
    """Configuration for search engine connection."""

    engine_type: str = Field(
        default="elasticsearch", description="Type of search engine"
    )
    host: str = Field(default="localhost", description="Search engine host")
    port: int = Field(default=9200, description="Search engine port")
    index: str = Field(default="library_catalog", description="Search index name")
    username: Optional[str] = Field(None, description="Authentication username")
    password: Optional[str] = Field(None, description="Authentication password")


class GeneratorConfig(BaseModel):
    """Configuration for data generation."""

    ai_model: str = Field(default="gpt-4", description="AI model to use for generation")
    api_key: Optional[str] = Field(None, description="API key for AI service")
    max_results: int = Field(
        default=10, description="Maximum number of results per query"
    )
    language: str = Field(default="en", description="Primary language for generation")


class LogfakerConfig(BaseModel):
    """Main configuration for Logfaker."""

    search_engine: SearchEngineConfig = Field(
        default_factory=lambda: SearchEngineConfig(
            engine_type="elasticsearch",
            host="localhost",
            port=9200,
            index="library_catalog",
            username=None,
            password=None,
        )
    )
    generator: GeneratorConfig = Field(
        default_factory=lambda: GeneratorConfig(
            ai_model="gpt-4", api_key=None, max_results=10, language="en"
        )
    )
    catalog_type: str = Field(
        default="library", description="Type of catalog system (library, retail, etc.)"
    )
