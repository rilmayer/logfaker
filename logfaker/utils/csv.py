"""CSV export utilities."""

import csv
import json
from pathlib import Path
from typing import List, Optional, Union

from logfaker.core.config import LogfakerConfig
from logfaker.core.models import Content, SearchLog, SearchQuery, UserProfile


class CsvExporter:
    """Handles exporting data to CSV format."""

    @staticmethod
    def _resolve_path(output_path: Union[str, Path], config: Optional[LogfakerConfig] = None) -> Path:
        """Resolve the output path using config if provided."""
        path = Path(output_path)
        if config and config.output_dir:
            # If output_path is just a filename, put it in output_dir
            # If output_path is absolute or contains directories, use as-is
            if len(path.parts) == 1:
                return config.output_dir / path
        return path

    @staticmethod
    def export_search_queries(
        queries: List[SearchQuery],
        output_path: Union[str, Path],
        config: Optional[LogfakerConfig] = None
    ) -> None:
        """Export search queries to CSV."""
        path = CsvExporter._resolve_path(output_path, config)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Query ID", "Query Content", "Category"])
            for query in queries:
                writer.writerow([query.query_id, query.query_content, query.category])

    @staticmethod
    def export_content(
        contents: List[Content],
        output_path: Union[str, Path],
        config: Optional[LogfakerConfig] = None
    ) -> None:
        """Export content to CSV."""
        path = CsvExporter._resolve_path(output_path, config)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Content ID", "Title", "Description", "Category"])
            for content in contents:
                writer.writerow(
                    [
                        content.content_id,
                        content.title,
                        content.description,
                        content.category,
                    ]
                )

    @staticmethod
    def export_users(
        users: List[UserProfile],
        output_path: Union[str, Path],
        config: Optional[LogfakerConfig] = None
    ) -> None:
        """Export user profiles to CSV."""
        path = CsvExporter._resolve_path(output_path, config)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["User ID", "Brief Explanation", "Profession", "Preferences"])
            for user in users:
                writer.writerow(
                    [
                        user.user_id,
                        user.brief_explanation,
                        user.profession,
                        ",".join(user.preferences),
                    ]
                )

    @staticmethod
    def export_search_logs(
        logs: List[SearchLog],
        output_path: Union[str, Path],
        config: Optional[LogfakerConfig] = None
    ) -> None:
        """Export search logs to CSV."""
        path = CsvExporter._resolve_path(output_path, config)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Query ID",
                "User ID",
                "Search Query",
                "Search Results (JSON)"
            ])
            for log in logs:
                writer.writerow([
                    log.query_id,
                    log.user_id,
                    log.search_query,
                    json.dumps([result.dict() for result in log.search_results], ensure_ascii=False)
                ])
