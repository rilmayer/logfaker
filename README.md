# Logfaker

Generate realistic test data for search engines, focusing on library catalog search systems.

## Installation

```bash
# Install using Poetry
poetry install
```

## Setup and Configuration

### OpenAI Credentials Setup

The package uses OpenAI for generating realistic content. You'll need to configure your OpenAI credentials:

```python
from logfaker.core.config import LogfakerConfig, GeneratorConfig

config = LogfakerConfig(
    generator=GeneratorConfig(
        api_key="your-openai-api-key",    # Required: OpenAI API key
        service_type="図書館の蔵書検索サービス",  # Optional: Defaults to "Book search service"
        language="ja",                     # Optional: Defaults to "en"
        ai_model="gpt-4"                  # Optional: Defaults to "gpt-4"
    )
)
```

### Elasticsearch Setup

1. Install and Start Elasticsearch:

   Ubuntu/Debian:
   ```bash
   sudo apt update
   sudo apt install elasticsearch
   sudo systemctl start elasticsearch
   ```

   MacOS:
   ```bash
   # Install using Homebrew
   brew tap elastic/tap
   brew install elastic/tap/elasticsearch-full
   
   # Start Elasticsearch
   brew services start elastic/tap/elasticsearch-full
   ```

2. Configure Elasticsearch Connection:
   ```python
   from logfaker.core.config import LogfakerConfig, SearchEngineConfig

   config = LogfakerConfig(
       search_engine=SearchEngineConfig(
           host="localhost",           # Elasticsearch host
           port=9200,                 # Elasticsearch port
           index="library_catalog",   # Index name
           username="your-username",  # Optional: For authentication
           password="your-password"   # Optional: For authentication
       )
   )
   ```

## Usage Example

```python
# Initialize configuration
config = LogfakerConfig(
    generator=GeneratorConfig(api_key="your-openai-api-key"),
    search_engine=SearchEngineConfig(host="localhost", port=9200)
)

# コンテンツの生成とインデックス作成
from logfaker.generators.content import ContentGenerator
from logfaker.generators.users import UserGenerator
from logfaker.generators.queries import QueryGenerator
from logfaker.search.elasticsearch import ElasticsearchEngine
from logfaker.utils.csv import CsvExporter

# コンテンツジェネレーターの作成
content_gen = ContentGenerator(config.generator)
contents = content_gen.generate_contents(count=50)  # 5カテゴリ x 10アイテム

# Elasticsearchへのインデックス作成
es = ElasticsearchEngine(config.search_engine)
for content in contents:
    es.index_content(content.content_id, content.dict())

# 検索の実行
results = es.search("人工知能", max_results=5)

# 検索ログの生成と出力
from logfaker.core.models import SearchLog
search_log = SearchLog(
    query_id=1,
    user_id=1001,
    search_query="人工知能",
    search_results=results,
    clicks=3,
    ctr=0.6
)

# CSVファイルへの出力
exporter = CsvExporter()
exporter.export_search_logs([search_log], "search_logs.csv")
```

## Output Formats

The package generates data in CSV format (出力形式):

```csv
# Content Format (コンテンツ形式)
Content ID,Title,Description,Category
1,"人工知能入門","AIの基礎から応用まで網羅的に解説するガイド","テクノロジー"

# User Profile Format (ユーザープロファイル形式)
User ID,Brief Explanation,Profession,Preferences
1001,"最新のテクノロジーと科学に興味を持つ大学院生","学生","人工知能, データサイエンス"

# Search Query Format (検索クエリ形式)
Query ID,Query Content,Category
1,"機械学習","テクノロジー"

# Search Log Format (検索ログ形式)
Query ID,User ID,Search Query,Search Results (JSON),Clicks,CTR
1,1001,"人工知能","[{\"title\": \"人工知能入門\", \"url\": \"https://library.example.com/book/1\"}]",3,0.6
```
