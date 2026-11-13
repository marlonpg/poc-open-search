"""Lesson 6 - Relevance: why is this result first?

_score is computed with BM25. Roughly, a document scores higher when:
  - the term appears MORE often in that field (term frequency)
  - the term is RARE across the whole index (inverse document frequency)
  - the field is SHORT (a match in a 3-word name beats one in a long description)

Tools to understand and tune ranking:
  highlight     -> show WHERE it matched
  explain=true  -> the full math behind a score
  ^boost        -> make one field matter more
  function_score-> mix business signals (rating, stock...) into the score
"""
import json

from common import INDEX, call, note, print_hits, title

title("1. Highlighting: show the matching fragments")
print_hits(call("POST", f"/{INDEX}/_search", {
    "query": {"multi_match": {"query": "waterproof outdoor", "fields": ["name", "description"]}},
    "highlight": {"fields": {"description": {}, "name": {}}, "pre_tags": ["**"], "post_tags": ["**"]},
}, show_response=False))

title("2. explain: how was the score of the top hit computed?")
result = call("POST", f"/{INDEX}/_search", {
    "query": {"match": {"name": "laptop"}},
    "explain": True,
    "size": 1,
}, show_response=False)
top = result["hits"]["hits"][0]
note(f"top hit: {top['_source']['name']} score={top['_score']:.3f}")
print(json.dumps(top["_explanation"], indent=2)[:2500], "\n...")

title("3. Boosting changes the ranking")
note("Without boost:")
print_hits(call("POST", f"/{INDEX}/_search", {
    "query": {"multi_match": {"query": "running", "fields": ["name", "tags", "description"]}},
}, show_response=False))
note("Description matches boosted x5 instead:")
print_hits(call("POST", f"/{INDEX}/_search", {
    "query": {"multi_match": {"query": "running", "fields": ["name", "tags", "description^5"]}},
}, show_response=False))

title("4. function_score: text relevance x product rating, and push out-of-stock down")
print_hits(call("POST", f"/{INDEX}/_search", {
    "query": {"function_score": {
        "query": {"match": {"description": "coffee espresso"}},
        "functions": [
            {"field_value_factor": {"field": "rating", "factor": 1, "modifier": "sqrt"}},
            {"filter": {"term": {"in_stock": False}}, "weight": 0.1},
        ],
        "score_mode": "multiply",
        "boost_mode": "multiply",
    }},
}, show_response=False), ("name", "rating", "in_stock"))
