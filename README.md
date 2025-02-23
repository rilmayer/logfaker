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
        ai_model="gpt4o-mini",            # Optional: Defaults to gpt4o-mini
        log_level="INFO"                  # Optional: Defaults to INFO
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

## Usage Example (使用例)

```python
from logfaker.core.config import LogfakerConfig, GeneratorConfig
from logfaker.generators.content import ContentGenerator
from logfaker.generators.users import UserGenerator
from logfaker.utils.csv import CsvExporter

# 設定の初期化
config = LogfakerConfig(
    generator=GeneratorConfig(
        api_key="your-openai-api-key",
        service_type="図書館の蔵書検索サービス",  # サービスタイプの指定
        language="ja",                     # 日本語コンテンツの生成
        log_level="INFO",                  # ログレベルの設定
        ai_model="gpt4o-mini"             # AIモデルの指定
    )
)

# コンテンツ生成とElasticsearchへのインデックス作成
content_gen = ContentGenerator(config.generator)
contents = content_gen.generate_contents(count=50)  # 生成されたカテゴリに基づいて50アイテムを生成

# Elasticsearchへのインデックス作成
es = ElasticsearchEngine(config.search_engine)
for content in contents:
    es.index_content(content.content_id, content.dict())

# カテゴリ一覧を取得してユーザー生成に利用
categories = content_gen._generate_categories()
user_gen = UserGenerator(config.generator)
users = user_gen.generate_users(count=10, categories=categories)  # カテゴリに基づいて10人のユーザーを生成

# ユーザーの興味に基づいて検索クエリを生成
query_gen = QueryGenerator(config.generator)
queries = []
search_logs = []

for user in users:
    # ユーザーごとに3つの検索クエリを生成
    user_queries = query_gen.generate_queries(user, count=3)
    queries.extend(user_queries)
    
    # 各クエリで検索を実行してログを生成
    for query in user_queries:
        results = es.search(query.query_content, max_results=5)
        
        # 検索ログの生成（クリック数とCTRはシミュレーション）
        search_log = SearchLog(
            query_id=query.query_id,
            user_id=user.user_id,
            search_query=query.query_content,
            search_results=results,
            clicks=2,  # シミュレートされたクリック数
            ctr=0.4    # シミュレートされたCTR
        )
        search_logs.append(search_log)

# CSVファイルへの出力
exporter = CsvExporter()
exporter.export_content(contents, "contents.csv")     # コンテンツをCSVに出力
exporter.export_users(users, "users.csv")            # ユーザープロファイルをCSVに出力
exporter.export_queries(queries, "queries.csv")      # 検索クエリをCSVに出力
exporter.export_search_logs(search_logs, "logs.csv") # 検索ログをCSVに出力

# 出力されるCSVの例

## contents.csv
# Content ID,Title,Description,Category
# 1,"人工知能入門","AIの基礎から応用まで網羅的に解説するガイド","テクノロジー"
# 2,"データサイエンスの実践","ビッグデータ分析の手法と実装","データサイエンス"
# ...

## users.csv
# User ID,Brief Explanation,Profession,Preferences
# 1,"最新のテクノロジーと科学に興味を持つ大学院生","学生","テクノロジー, データサイエンス"
# 2,"文学と歴史に造詣が深い図書館司書","司書","文学, 歴史"
# ...
```

このワークフローでは以下のような処理が行われます：

1. **設定の初期化**:
   - サービスタイプを「図書館の蔵書検索サービス」に設定
   - 日本語でのコンテンツ生成を指定
   - ログレベルをINFOに設定
   - AIモデルをgpt4o-miniに指定

2. **コンテンツ生成とインデックス作成**:
   - サービスタイプに基づいて約100個のカテゴリを生成
   - 各カテゴリに対して最大10個のコンテンツを生成
   - 生成過程はログに詳細に記録
   - 生成されたコンテンツをElasticsearchにインデックス

3. **ユーザー生成**:
   - 生成されたカテゴリを利用してユーザープロファイルを作成
   - 各ユーザーは少なくとも1つのカテゴリに興味を持つ
   - ユーザーの興味は実際のカテゴリから選択

4. **検索クエリ生成と実行**:
   - ユーザーの興味に基づいて検索クエリを生成
   - 各ユーザーにつき3つの検索クエリを生成
   - 生成されたクエリでElasticsearch検索を実行
   - 検索結果からクリック数とCTRをシミュレート

5. **データ出力**:
   - 生成されたコンテンツをCSVに出力
   - ユーザープロファイルをCSVに出力
   - 検索クエリをCSVに出力
   - 検索ログ（結果、クリック数、CTR）をCSVに出力
   - すべてのCSVファイルは日本語を正しく処理

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
