# Logfaker

Logfakerは、検索エンジン向けの現実的なテストデータを生成するツールです。このツールは、与えられた設定に基づいてコンテンツ、ユーザー、検索クエリを生成し、Elasticsearchなどの検索エンジンと連携してそれらの検索ログを出力することができます。これにより、検索エンジンのテストやデモンストレーションに必要なデータを簡単に準備することが可能です。

## インストールとセットアップ

### 必要要件

- Python 3.8 以上
- OpenAI API キー
- Elasticsearch (オプション、検索機能を使用する場合)

### インストール

pip を使用してインストールできます：

```bash
pip install logfaker
```

開発用インストール：

```bash
# リポジトリをクローン
git clone https://github.com/rilmayer/logfaker.git
cd logfaker

# Poetry を使用してインストール
poetry install
```

### OpenAI 認証情報の設定

このパッケージは現実的なコンテンツを生成するために OpenAI を使用します。以下のように OpenAI の認証情報を設定してください：

```python
from logfaker.core.config import LogfakerConfig, GeneratorConfig

config = LogfakerConfig(
    generator=GeneratorConfig(
        api_key="your-openai-api-key",    # 必須: OpenAI API キー
        service_type="図書館の蔵書検索サービス",  # オプション: デフォルトは "Book search service"
        language="ja",                     # オプション: デフォルトは "en"
        ai_model="gpt-4o-mini",            # オプション: デフォルトは gpt-4o-mini
        log_level="INFO"                  # オプション: デフォルトは INFO
    )
)
```

### Elasticsearch のセットアップ

1. Elasticsearch のインストールと起動:

   Ubuntu/Debian:
   ```bash
   sudo apt update
   sudo apt install elasticsearch
   sudo systemctl start elasticsearch
   ```

   MacOS:
   ```bash
   # Homebrew を使用してインストール
   brew tap elastic/tap
   brew install elastic/tap/elasticsearch-full
   
   # Elasticsearch を起動
   brew services start elastic/tap/elasticsearch-full
   ```

2. インデックスの設定:
   ```python
   from logfaker.core.config import LogfakerConfig, SearchEngineConfig
   from logfaker.search.elasticsearch import ElasticsearchEngine

   # 接続設定
   config = LogfakerConfig(
       search_engine=SearchEngineConfig(
           host="localhost",           # Elasticsearch ホスト
           port=9200,                 # Elasticsearch ポート
           index="library_catalog",   # インデックス名
           username="your-username",  # オプション: 認証用
           password="your-password"   # オプション: 認証用
       )
   )

   # 検索エンジンとインデックスのセットアップ
   es = ElasticsearchEngine(config.search_engine)
   if not es.is_healthy():
       raise RuntimeError("Elasticsearch が利用できません")
   
   # 必要に応じて既存のインデックスを削除
   es.setup_index(force=True)  # force=True で既存のインデックスを削除
   ```

### 出力ディレクトリの設定

すべての出力ファイルを一つのディレクトリに設定できます：

```python
config = LogfakerConfig(
    output_dir="出力先ディレクトリのパス"  # すべての CSV ファイルがここに保存されます
)
```

output_dir が設定されている場合、ファイル名のみのパスはこのディレクトリに配置されます：
- contents.csv -> 出力先ディレクトリのパス/contents.csv
- users.csv -> 出力先ディレクトリのパス/users.csv
など

絶対パスやディレクトリを含むパスはそのまま使用されます。

## 使用方法

### 基本的な使用例

```python
from logfaker.core.config import LogfakerConfig, GeneratorConfig
from logfaker.generators.content import ContentGenerator
from logfaker.generators.users import UserGenerator
from logfaker.utils.csv import CsvExporter

# 設定の初期化
config = LogfakerConfig(
    generator=GeneratorConfig(
        api_key="your-openai-api-key",
        service_type="図書館の蔵書検索サービス",
        language="ja",
        log_level="INFO",
        ai_model="gpt4o-mini"
    )
)

# コンテンツ生成と Elasticsearch へのインデックス作成
content_gen = ContentGenerator(config.generator)
contents = content_gen.generate_contents(count=50)

# Elasticsearch のセットアップ
es = ElasticsearchEngine(config.search_engine)
if not es.setup_index(force=True):
    raise RuntimeError("Elasticsearch インデックスのセットアップに失敗しました")

# コンテンツを Elasticsearch にインデックス
for content in contents:
    es.index_content(content.content_id, content.dict())

# ユーザー生成
user_gen = UserGenerator(config.generator)
users = user_gen.generate_users(count=10)

# ユーザーの興味に基づいて検索クエリを生成
query_gen = QueryGenerator(config.generator)
queries = []
search_logs = []

for user in users:
    # ユーザーごとに3つの検索クエリを生成
    user_queries = query_gen.generate_queries(user, count=3)
    queries.extend(user_queries)
    
    # 検索を実行してログを生成
    for query in user_queries:
        results = es.search(query.query_content, max_results=5)
        search_log = SearchLog(
            query_id=query.query_id,
            user_id=user.user_id,
            search_query=query.query_content,
            search_results=results
        )
        search_logs.append(search_log)

# CSV ファイルへの出力
exporter = CsvExporter()
exporter.export_content(contents, "contents.csv")
exporter.export_users(users, "users.csv")
exporter.export_search_queries(queries, "queries.csv")
exporter.export_search_logs(search_logs, "logs.csv")
```

### CSV ファイルの再利用

パッケージは以前に生成されたコンテンツとユーザープロファイルを再利用できます：

```python
# コンテンツを生成（contents.csv が存在する場合は再利用）
contents = content_gen.generate_contents(count=50, reuse_file=True)  # デフォルト: reuse_file=True

# ユーザーを生成（users.csv が存在する場合は再利用）
users = user_gen.generate_users(count=10, reuse_file=True)

# 強制的に再生成する場合は reuse_file=False を設定
contents = content_gen.generate_contents(count=50, reuse_file=False)
users = user_gen.generate_users(count=10, reuse_file=False)
```

## テスト

Poetry を使用してテストを実行：

```bash
# 開発依存関係をインストール
poetry install

# すべてのテストを実行
poetry run pytest

# ユニットテストのみ実行
poetry run pytest -v -m "not integration"

# 統合テストを実行（OPENAI_API_KEY が必要）
export OPENAI_API_KEY="your-openai-api-key"
poetry run pytest -v -m integration
```

注意: 統合テストには有効な OpenAI API キーが必要です。`OPENAI_API_KEY` が設定されていない場合、`@pytest.mark.integration` でマークされたテストはスキップされます。

### テストのカテゴリ

1. **ユニットテスト**:
   - コンテンツ生成テスト
   - OpenAI API をモックしたクエリ生成テスト
   - ユーザープロファイル生成テスト
   - ファイル再利用機能テスト

2. **統合テスト**:
   - 実際の OpenAI API を使用した統合テスト
   - 実データを使用したファイル再利用機能
   - エラーハンドリングテスト

## 出力形式

パッケージは以下の CSV 形式でデータを生成します：

```csv
# コンテンツ形式
Content ID,Title,Description,Category
1,"人工知能入門","AIの基礎から応用まで網羅的に解説するガイド","テクノロジー"

# ユーザープロファイル形式
User ID,Brief Explanation,Profession,Preferences
1001,"最新のテクノロジーと科学に興味を持つ大学院生","学生","人工知能, データサイエンス"

# 検索クエリ形式
Query ID,Query Content,Category
1,"機械学習","テクノロジー"

# 検索ログ形式
Query ID,User ID,Search Query,Search Results (JSON)
1,1001,"人工知能","[{\"title\": \"人工知能入門\", \"url\": \"https://library.example.com/book/1\"}]"
```
