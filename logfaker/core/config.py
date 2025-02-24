"""Configuration settings for Logfaker."""

from pathlib import Path
from typing import Dict, Optional, Union

from pydantic import BaseModel, Field


class SearchEngineConfig(BaseModel):
    """Configuration for search engine connection."""

    engine_type: str = Field(
        default="elasticsearch", description="Type of search engine"
    )
    language: str = Field(default="en", description="Primary language for search")
    host: str = Field(default="localhost", description="Search engine host")
    port: int = Field(default=9200, description="Search engine port")
    index: str = Field(default="library_catalog", description="Search index name")
    username: Optional[str] = Field(None, description="Authentication username")
    password: Optional[str] = Field(None, description="Authentication password")


class GeneratorConfig(BaseModel):
    """Configuration for data generation."""

    ai_model: str = Field(default="gpt-4o-mini", description="AI model to use for generation")
    api_key: Optional[str] = Field(None, description="API key for AI service")
    max_results: int = Field(
        default=10, description="Maximum number of results per query"
    )
    language: str = Field(default="en", description="Primary language for generation")
    service_type: str = Field(
        default="Book search service",
        description="Type of search service (e.g., library catalog)"
    )
    log_level: str = Field(default="INFO", description="Logging level for generators")
    output_dir: Optional[Path] = Field(
        default=None,
        description="Directory for output files. If None, uses current directory"
    )


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
            ai_model="gpt-4o-mini",
            api_key=None,
            max_results=10,
            language="en",
            service_type="Book search service",
            log_level="INFO"
        )
    )
    catalog_type: str = Field(
        default="library", description="Type of catalog system (library, retail, etc.)"
    )
    output_dir: Optional[Path] = Field(
        default=None,
        description="Directory for all output files. If None, uses current directory"
    )
