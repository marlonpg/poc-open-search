"""Lesson 2 - Creating an index with settings and a mapping.

The MAPPING is the schema: it tells OpenSearch the type of each field and
HOW to index it. The most important distinction to learn:

  text    -> full-text. The value is run through an ANALYZER which splits it
             into tokens ("Wireless Noise-Cancelling Headphones" ->
             [wireless, noise, cancelling, headphones]). Good for search
             boxes. Not good for exact match, sorting or aggregations.
  keyword -> stored as ONE exact token. Good for filters, sorting,
             aggregations (facets), IDs, tags, status codes.

You can have both on the same field using "fields" (multi-fields):
  name        -> text      (search it)
  name.raw    -> keyword   (sort / aggregate on it)

If you don't define a mapping, OpenSearch guesses one ("dynamic mapping").
Handy for exploring, risky in production: a field's type cannot be changed
after data is indexed - you have to create a new index and reindex.
"""
from common import INDEX, call, note, title

title("1. Delete the index if it exists (so the lesson is repeatable)")
call("DELETE", f"/{INDEX}")

title("2. Create the index with settings + mapping")
note("number_of_replicas=0 because we only have 1 node -> health stays green.")
call("PUT", f"/{INDEX}", {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                # A custom analyzer: standard tokenizer + lowercase + remove
                # English stopwords + stemming ("running" -> "run").
                "english_custom": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "english_stop", "english_stemmer"],
                }
            },
            "filter": {
                "english_stop": {"type": "stop", "stopwords": "_english_"},
                "english_stemmer": {"type": "stemmer", "language": "english"},
            },
        },
    },
    "mappings": {
        "dynamic": "strict",  # reject documents with unknown fields
        "properties": {
            "name": {
                "type": "text",
                "analyzer": "english_custom",
                "fields": {"raw": {"type": "keyword"}},
            },
            "description": {"type": "text", "analyzer": "english_custom"},
            "category": {"type": "keyword"},
            "brand": {"type": "keyword"},
            "tags": {"type": "keyword"},
            "price": {"type": "float"},
            "rating": {"type": "float"},
            "stock": {"type": "integer"},
            "in_stock": {"type": "boolean"},
            "created_at": {"type": "date"},
        },
    },
})

title("3. Read back the mapping")
call("GET", f"/{INDEX}/_mapping")

title("4. See what an ANALYZER does to text (the _analyze API)")
note("This is THE key to understanding why a search matches or not.")
sample = "The Runners are running quickly with Wireless Headphones!"
note("standard analyzer: only splits + lowercases")
call("POST", "/_analyze", {"analyzer": "standard", "text": sample})
note("our english_custom analyzer: also removes 'the/are/with' and stems")
call("POST", f"/{INDEX}/_analyze", {"analyzer": "english_custom", "text": sample})
note("keyword analyzer: the whole string is ONE token")
call("POST", "/_analyze", {"analyzer": "keyword", "text": sample})
