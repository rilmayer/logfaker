# Logfaker

[日本語のREADMEはこちら](README.ja.md)

Logfaker is a tool for generating realistic test data for search engines. It generates content, users, and search queries based on the provided configurations, and can output search logs by integrating with search engines like Elasticsearch. This makes it easy to prepare the necessary data for testing and demonstration purposes for search engines.

## Installation & Setup

### Requirements

- Python 3.8 or higher
- OpenAI API key
- Elasticsearch (optional, for search functionality)

### Installation

You can install logfaker using pip:

```bash
pip install logfaker
```

For development installation:

```bash
# Clone the repository
git clone https://github.com/rilmayer/logfaker.git
cd logfaker

# Install using Poetry
poetry install
```

### OpenAI Credentials Setup

The package uses OpenAI for generating realistic content. Configure your OpenAI credentials:

```python
from logfaker.core.config import LogfakerConfig, GeneratorConfig

config = LogfakerConfig(
    generator=GeneratorConfig(
        api_key="your-openai-api-key",    # Required: OpenAI API key
        service_type="Book search service", # Optional: Defaults to "Book search service"
        language="en",                     # Optional: Defaults to "en"
        ai_model="gpt-4o-mini",            # Optional: Defaults to gpt-4o-mini
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

2. Configure and Set Up Index:
   ```python
   from logfaker.core.config import LogfakerConfig, SearchEngineConfig
   from logfaker.search.elasticsearch import ElasticsearchEngine

   # Configure connection
   config = LogfakerConfig(
       search_engine=SearchEngineConfig(
           host="localhost",           # Elasticsearch host
           port=9200,                 # Elasticsearch port
           index="library_catalog",   # Index name
           username="your-username",  # Optional: For authentication
           password="your-password"   # Optional: For authentication
       )
   )

   # Set up search engine and index
   es = ElasticsearchEngine(config.search_engine)
   if not es.is_healthy():
       raise RuntimeError("Elasticsearch is not available")
   
   # Delete existing index if needed
   es.setup_index(force=True)  # force=True will delete existing index
   ```

### Output Directory Configuration

Configure a single directory for all output files:

```python
config = LogfakerConfig(
    output_dir="path/to/output/directory"  # All CSV files will be saved here
)
```

When output_dir is set, any filename-only paths will be placed in this directory:
- contents.csv -> path/to/output/directory/contents.csv
- users.csv -> path/to/output/directory/users.csv
etc.

Absolute paths or paths with directories are used as-is.

## Usage

### Basic Usage Example

```python
from logfaker.core.config import LogfakerConfig, GeneratorConfig
from logfaker.generators.content import ContentGenerator
from logfaker.generators.users import UserGenerator
from logfaker.utils.csv import CsvExporter

# Initialize configuration
config = LogfakerConfig(
    generator=GeneratorConfig(
        api_key="your-openai-api-key",
        service_type="Book search service",
        language="en",
        log_level="INFO",
        ai_model="gpt4o-mini"
    )
)

# Generate content and create Elasticsearch index
content_gen = ContentGenerator(config.generator)
contents = content_gen.generate_contents(count=50)

# Set up Elasticsearch
es = ElasticsearchEngine(config.search_engine)
if not es.setup_index(force=True):
    raise RuntimeError("Failed to set up Elasticsearch index")

# Index content to Elasticsearch
for content in contents:
    es.index_content(content.content_id, content.dict())

# Generate users
user_gen = UserGenerator(config.generator)
users = user_gen.generate_users(count=10)

# Generate search queries based on user interests
query_gen = QueryGenerator(config.generator)
queries = []
search_logs = []

for user in users:
    # Generate 3 search queries per user
    user_queries = query_gen.generate_queries(user, count=3)
    queries.extend(user_queries)
    
    # Execute searches and generate logs
    for query in user_queries:
        results = es.search(query.query_content, max_results=5)
        search_log = SearchLog(
            query_id=query.query_id,
            user_id=user.user_id,
            search_query=query.query_content,
            search_results=results
        )
        search_logs.append(search_log)

# Export to CSV files
exporter = CsvExporter()
exporter.export_content(contents, "contents.csv")
exporter.export_users(users, "users.csv")
exporter.export_search_queries(queries, "queries.csv")
exporter.export_search_logs(search_logs, "logs.csv")
```

### CSV File Reuse

The package can reuse previously generated content and user profiles:

```python
# Generate content (will reuse contents.csv if it exists)
contents = content_gen.generate_contents(count=50, reuse_file=True)  # Default: reuse_file=True

# Generate users (will reuse users.csv if it exists)
users = user_gen.generate_users(count=10, reuse_file=True)

# Force regeneration by setting reuse_file=False
contents = content_gen.generate_contents(count=50, reuse_file=False)
users = user_gen.generate_users(count=10, reuse_file=False)
```

## Testing

Run the tests using Poetry:

```bash
# Install with development dependencies
poetry install

# Run all tests
poetry run pytest

# Run only unit tests
poetry run pytest -v -m "not integration"

# Run integration tests (requires OPENAI_API_KEY)
export OPENAI_API_KEY="your-openai-api-key"
poetry run pytest -v -m integration
```

Note: Integration tests require a valid OpenAI API key. Tests marked with `@pytest.mark.integration` will be skipped if `OPENAI_API_KEY` is not set.

### Test Categories

1. **Unit Tests**:
   - Content generation tests
   - Query generation tests with mocked OpenAI API
   - User profile generation tests
   - File reuse functionality tests

2. **Integration Tests**:
   - Real OpenAI API integration tests
   - File reuse functionality with real data
   - Error handling tests

## Output Formats

The package generates the following CSV formats:

```csv
# Content Format
Content ID,Title,Description,Category
1,"Introduction to AI","A comprehensive guide to AI fundamentals","Technology"

# User Profile Format
User ID,Brief Explanation,Profession,Preferences
1001,"Graduate student interested in technology and science","Student","AI, Data Science"

# Search Query Format
Query ID,Query Content,Category
1,"machine learning","Technology"

# Search Log Format
Query ID,User ID,Search Query,Search Results (JSON)
1,1001,"artificial intelligence","[{\"title\": \"Introduction to AI\", \"url\": \"https://library.example.com/book/1\"}]"
```
