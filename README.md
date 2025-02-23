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
        api_key="your-openai-api-key",  # Required: Your OpenAI API key
        ai_model="gpt-4",               # Optional: Defaults to gpt-4
        language="en"                   # Optional: Defaults to en
    )
)
```

### Elasticsearch Setup

1. Install and Start Elasticsearch:
   ```bash
   # Example for Ubuntu/Debian
   sudo apt update
   sudo apt install elasticsearch
   sudo systemctl start elasticsearch
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

# Generate and index content
from logfaker.generators.content import ContentGenerator
from logfaker.search.elasticsearch import ElasticsearchEngine

# Create content generator
content_gen = ContentGenerator(config.generator)
contents = content_gen.generate_contents(count=5)

# Index content in Elasticsearch
es = ElasticsearchEngine(config.search_engine)
for content in contents:
    es.index_content(content.content_id, content.dict())

# Search indexed content
results = es.search("technology", max_results=5)
```

## Output Formats

The package generates data in CSV format:

```csv
# Content Format
Content ID,Title,Description,Category
1,"Introduction to AI","A comprehensive guide...","Technology"

# User Profile Format
User ID,Brief Explanation,Profession,Preferences
1001,"A curious student with a passion for emerging technologies","student","technology, science fiction"

# Search Query Format
Query ID,Query Content,Category
1,"technology","General"

# Search Log Format
Query ID,User ID,Search Query,Search Results (JSON),Clicks,CTR
1,1001,"technology","[{\"title\": \"AI Guide\"}]",3,0.5
```
