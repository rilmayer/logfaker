import logging
import os
import warnings
from elasticsearch import ElasticsearchWarning

from logfaker.core.config import (GeneratorConfig, LogfakerConfig,
                                 SearchEngineConfig)
from logfaker.core.models import SearchLog
from logfaker.generators.content import ContentGenerator
from logfaker.generators.queries import QueryGenerator
from logfaker.generators.users import UserGenerator
from logfaker.search.elasticsearch import ElasticsearchEngine
from logfaker.utils.csv import CsvExporter

# ロギングの設定
logging.basicConfig(level=logging.INFO)
warnings.filterwarnings("ignore", category=ElasticsearchWarning)

# フォルダを作成するパスを指定
DIRECTORY_PATH = "examples/library_book_small/"


def create_directory(path):
    """指定されたパスにフォルダを作成します。"""
    if not os.path.exists(path):
        os.makedirs(path)


def setup_config():
    """設定を初期化します。"""
    return LogfakerConfig(
        generator=GeneratorConfig(
            api_key=os.getenv("OPENAI_API_KEY"),
            service_type="公共図書館の蔵書検索サービス",
            language="ja",
            ai_model="gpt-4o-mini",
            log_level="INFO",
            output_dir=DIRECTORY_PATH,
        ),
        search_engine=SearchEngineConfig(
            language="ja", host="localhost", port=9200, index="library_catalog"
        ),
    )


def generate_and_export_contents(config):
    """コンテンツを生成し、エクスポートします。"""
    content_gen = ContentGenerator(config.generator)
    contents = content_gen.generate_contents(count=10)
    return contents


def setup_elasticsearch(config):
    """Elasticsearchのインデックスをセットアップします。"""
    try:
        es = ElasticsearchEngine(config.search_engine)
        # Check if Elasticsearch is available
        if not es.is_healthy():
            logging.warning("Elasticsearch is not available. Skipping Elasticsearch setup.")
            return None
        
        # Check if kuromoji is installed
        try:
            plugins = es.client.cat.plugins(format="json")
            kuromoji_installed = any(plugin.get("component") == "analysis-kuromoji" for plugin in plugins)
            if not kuromoji_installed:
                logging.warning("Kuromoji is not installed in Elasticsearch. Japanese language support may be limited.")
                # Note: Installing plugins requires Elasticsearch restart, which is beyond the scope of this script
        except Exception as e:
            logging.warning(f"Failed to check Elasticsearch plugins: {e}")
        
        # Setup index
        if not es.setup_index(force=True):
            logging.error("Failed to set up Elasticsearch index")
            return None
        return es
    except Exception as e:
        logging.warning(f"Failed to connect to Elasticsearch: {e}")
        return None


def index_contents(es, contents):
    """コンテンツをElasticsearchにインデックスします。"""
    if es is None:
        return
    
    for content in contents:
        es.index_content(content.content_id, content.dict())


def generate_and_export_users(config):
    """ユーザーを生成し、エクスポートします。"""
    user_gen = UserGenerator(config.generator)
    users = user_gen.generate_users(count=5)
    return users


def generate_search_logs(es, users, config):
    """検索ログを生成し、エクスポートします。"""
    query_gen = QueryGenerator(config.generator)
    queries = []
    search_logs = []

    for user in users:
        user_queries = query_gen.generate_queries(user, count=1)
        queries.extend(user_queries)

        if es is not None:
            for query in user_queries:
                results = es.search(query.query_content, max_results=5)
                search_log = SearchLog(
                    query_id=query.query_id,
                    user_id=user.user_id,
                    search_query=query.query_content,
                    search_results=results,
                )
                search_logs.append(search_log)
        else:
            # If Elasticsearch is not available, create empty search logs
            for query in user_queries:
                search_log = SearchLog(
                    query_id=query.query_id,
                    user_id=user.user_id,
                    search_query=query.query_content,
                    search_results=[],
                )
                search_logs.append(search_log)

    exporter = CsvExporter()
    exporter.export_search_queries(queries, DIRECTORY_PATH + "queries.csv")
    exporter.export_search_logs(search_logs, DIRECTORY_PATH + "logs.csv")
    return queries


def main():
    create_directory(DIRECTORY_PATH)
    exporter = CsvExporter()
    config = setup_config()
    contents = generate_and_export_contents(config)
    exporter.export_content(contents, DIRECTORY_PATH + "contents.csv")
    es = setup_elasticsearch(config)
    index_contents(es, contents)
    users = generate_and_export_users(config)
    exporter.export_users(users, DIRECTORY_PATH + "users.csv")
    queries = generate_search_logs(es, users, config)
    
    logging.info(f"Generated {len(contents)} content items")
    logging.info(f"Generated {len(users)} users")
    logging.info(f"Generated {len(queries)} queries")
    logging.info(f"Output files saved to {DIRECTORY_PATH}")


if __name__ == "__main__":
    main()
