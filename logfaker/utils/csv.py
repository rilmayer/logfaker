"""CSV export utilities."""
import csv
import json
from pathlib import Path
from typing import List, Union

from logfaker.core.models import (BookContent, SearchLog, SearchQuery,
                                UserProfile)


class CsvExporter:
    """Handles exporting data to CSV format."""

    @staticmethod
    def export_search_queries(
        queries: List[SearchQuery],
        output_path: Union[str, Path]
    ) -> None:
        """Export search queries to CSV."""
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Query ID', 'Query Content', 'Category'])
            for query in queries:
                writer.writerow([
                    query.query_id,
                    query.query_content,
                    query.category
                ])

    @staticmethod
    def export_user_content(
        contents: List[BookContent],
        users: List[UserProfile],
        output_path: Union[str, Path]
    ) -> None:
        """Export user-generated content to CSV."""
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Content ID', 'User ID', 'User Attributes', 'Content'])
            for content, user in zip(contents, users):
                writer.writerow([
                    content.content_id,
                    user.user_id,
                    user.to_json_str(),
                    content.description
                ])

    @staticmethod
    def export_search_logs(
        logs: List[SearchLog],
        output_path: Union[str, Path]
    ) -> None:
        """Export search logs to CSV."""
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Query ID', 'User ID', 'Search Query',
                'Search Results (JSON)', 'Clicks', 'CTR'
            ])
            for log in logs:
                writer.writerow([
                    log.query_id,
                    log.user_id,
                    log.search_query,
                    json.dumps([result.dict() for result in log.search_results]),
                    log.clicks,
                    log.ctr
                ])
