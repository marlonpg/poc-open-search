"""Lesson 7 - Changing data, and changing the schema safely.

  POST /index/_update/<id>    -> partial update (merge fields, or a script)
  POST /index/_update_by_query-> update every doc that matches a query
  DELETE /index/_doc/<id>     -> delete one doc
  POST /index/_delete_by_query-> delete every doc that matches a query

Documents are immutable on disk: an "update" really = read + reindex a new
version. That's why _version increments.

Mapping changes: you can ADD new fields, but you cannot change an existing
field's type. The production pattern is:
  1. create a new index (products_v2) with the new mapping
  2. _reindex products_v1 -> products_v2
  3. switch an ALIAS ("products_live") atomically from v1 to v2
Your application only ever talks to the alias, so there's no downtime.
"""
from common import INDEX, call, note, print_hits, title

title("1. Partial update: change price of product 4")
call("POST", f"/{INDEX}/_update/4?refresh=true", {"doc": {"price": 49.9}})
call("GET", f"/{INDEX}/_doc/4?_source=name,price")

title("2. Scripted update: decrement stock by 1 (painless scripting language)")
call("POST", f"/{INDEX}/_update/4?refresh=true", {
    "script": {"source": "ctx._source.stock -= params.qty", "params": {"qty": 1}}
})
call("GET", f"/{INDEX}/_doc/4?_source=name,stock")

title("3. update_by_query: 10% discount on every 'kitchen' product")
call("POST", f"/{INDEX}/_update_by_query?refresh=true", {
    "query": {"term": {"category": "kitchen"}},
    "script": {"source": "ctx._source.price = Math.round(ctx._source.price * 90) / 100.0"},
})

title("4. Delete one document, then confirm it's gone")
call("PUT", f"/{INDEX}/_doc/temp?refresh=true", {"name": "Temporary item", "category": "misc", "price": 1})
call("DELETE", f"/{INDEX}/_doc/temp?refresh=true")
call("GET", f"/{INDEX}/_doc/temp")

title("5. Reindex into a new index + alias switch (zero-downtime schema change)")
note("Imagine we want 'brand' to also be full-text searchable.")
call("DELETE", "/products_v2", show_response=False)
mapping = call("GET", f"/{INDEX}/_mapping", show_response=False)[INDEX]["mappings"]
settings = call("GET", f"/{INDEX}/_settings", show_response=False)[INDEX]["settings"]["index"]
mapping["properties"]["brand"] = {"type": "keyword", "fields": {"text": {"type": "text"}}}
call("PUT", "/products_v2", {
    "settings": {"number_of_shards": 1, "number_of_replicas": 0, "analysis": settings["analysis"]},
    "mappings": mapping,
}, show_response=False)
call("POST", "/_reindex?refresh=true", {"source": {"index": INDEX}, "dest": {"index": "products_v2"}})

note("Before: the app's alias 'products_live' points at the old index")
call("POST", "/_aliases", {"actions": [{"add": {"index": INDEX, "alias": "products_live"}}]})
note("Switch: remove from old + add to v2 in ONE atomic call")
call("POST", "/_aliases", {"actions": [
    {"remove": {"index": INDEX, "alias": "products_live"}},
    {"add": {"index": "products_v2", "alias": "products_live"}},
]})
call("GET", "/_cat/aliases?v")

note("Search through the alias using the new brand.text field:")
print_hits(call("POST", "/products_live/_search", {"query": {"match": {"brand.text": "trailhead"}}},
                show_response=False), ("name", "brand"))
