# Dev Tools cheat sheet

Open http://localhost:5601 → menu ☰ → **Management → Dev Tools**.
Paste any block below and press ▶ (or Ctrl+Enter). Run `python lessons/03_index_documents.py` first so the `products` index has data.

```
# Cluster
GET _cluster/health
GET _cat/indices?v
GET _cat/shards?v

# Index structure
GET products/_mapping
GET products/_settings
POST products/_analyze
{ "analyzer": "english_custom", "text": "Running shoes for runners" }

# Get / count
GET products/_doc/1
GET products/_count

# Full-text search
GET products/_search
{
  "query": { "match": { "description": "battery" } }
}

# Bool query: text + filters
GET products/_search
{
  "query": {
    "bool": {
      "must":   [ { "match": { "name": "headphones" } } ],
      "filter": [ { "term": { "in_stock": true } },
                  { "range": { "price": { "lte": 200 } } } ]
    }
  }
}

# Aggregation: average price per category
GET products/_search
{
  "size": 0,
  "aggs": {
    "by_category": {
      "terms": { "field": "category" },
      "aggs": { "avg_price": { "avg": { "field": "price" } } }
    }
  }
}

# Partial update
POST products/_update/1
{ "doc": { "price": 199.99 } }

# SQL (the SQL plugin ships with OpenSearch)
POST _plugins/_sql
{ "query": "SELECT category, AVG(price) FROM products GROUP BY category" }

# PPL (Piped Processing Language)
POST _plugins/_ppl
{ "query": "source=products | where price > 100 | stats count() by brand" }
```

Tip: in Dev Tools, click the 🔧 next to a request → **Copy as cURL** to see the raw HTTP call.
