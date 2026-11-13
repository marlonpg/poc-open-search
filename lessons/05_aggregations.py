"""Lesson 5 - Aggregations (analytics / facets / GROUP BY).

Aggregations compute stats over the documents matched by the query.
They run on keyword / numeric / date fields (not on analyzed text).

  bucket aggs -> split docs into groups   (terms, range, date_histogram)
  metric aggs -> compute a number         (avg, sum, min, max, stats, cardinality)
Bucket aggs can contain sub-aggregations -> "avg price per category".

Tip: "size": 0 means "don't return hits, I only want the aggregations".
"""
import json

from common import INDEX, call, note, title


def aggs(body):
    result = call("POST", f"/{INDEX}/_search", body, show_response=False)
    print(json.dumps(result["aggregations"], indent=2))


title("1. terms: count products per category (like GROUP BY category)")
aggs({"size": 0, "aggs": {"by_category": {"terms": {"field": "category"}}}})

title("2. Metrics over the whole index")
aggs({"size": 0, "aggs": {
    "price_stats": {"stats": {"field": "price"}},
    "distinct_brands": {"cardinality": {"field": "brand"}},
}})

title("3. Sub-aggregation: average price and rating per category, sorted by avg price")
aggs({"size": 0, "aggs": {"by_category": {
    "terms": {"field": "category", "order": {"avg_price": "desc"}},
    "aggs": {
        "avg_price": {"avg": {"field": "price"}},
        "avg_rating": {"avg": {"field": "rating"}},
    },
}}})

title("4. range buckets: price bands")
aggs({"size": 0, "aggs": {"price_bands": {"range": {"field": "price", "ranges": [
    {"key": "cheap", "to": 50},
    {"key": "mid", "from": 50, "to": 200},
    {"key": "premium", "from": 200},
]}}}})

title("5. date_histogram: products created per quarter")
aggs({"size": 0, "aggs": {"per_quarter": {
    "date_histogram": {"field": "created_at", "calendar_interval": "quarter", "format": "yyyy-QQQ"}
}}})

title("6. Search + facets together (what an e-commerce sidebar does)")
note("Query narrows to 'wireless'; aggs then describe only those hits.")
result = call("POST", f"/{INDEX}/_search", {
    "query": {"match": {"tags": "wireless"}},
    "_source": ["name"],
    "aggs": {
        "brands": {"terms": {"field": "brand"}},
        "in_stock": {"terms": {"field": "in_stock"}},
    },
}, show_response=False)
print("hits:", [h["_source"]["name"] for h in result["hits"]["hits"]])
print(json.dumps(result["aggregations"], indent=2))
