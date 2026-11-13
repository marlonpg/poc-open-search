"""Lesson 4 - Searching with the Query DSL.

All searches go to  GET/POST /<index>/_search  with a JSON body.

Two families of queries:
  FULL-TEXT (match, match_phrase, multi_match)
     -> the query text is analyzed with the field's analyzer, then matched
        token by token. Results get a relevance _score (BM25 algorithm).
  TERM-LEVEL (term, terms, range, exists, prefix)
     -> exact values, NOT analyzed. Use on keyword / number / date / boolean.

QUERY context vs FILTER context (inside a "bool" query):
  must / should   -> affects the score ("how well does it match?")
  filter/must_not -> yes/no only, no scoring, CACHED -> faster.
  Rule of thumb: what the user typed -> must; facets/checkboxes -> filter.
"""
from common import INDEX, call, note, print_hits, title


def search(body, fields=("name", "category", "price")):
    print_hits(call("POST", f"/{INDEX}/_search", body, show_response=False), fields)


title("1. match_all: everything (default returns 10 hits)")
search({"query": {"match_all": {}}, "size": 5})

title("2. match: full-text search. Note the stemming: 'run' finds 'running'")
note("The stemmer turned 'running' into 'run' at index time, and the query too.")
search({"query": {"match": {"description": "run"}}})

title("3. match with several words = OR by default")
search({"query": {"match": {"name": "wireless headphones"}}})
note("Use operator=and to require all words:")
search({"query": {"match": {"name": {"query": "wireless headphones", "operator": "and"}}}})

title("4. match_phrase: words must appear together, in order")
search({"query": {"match_phrase": {"description": "heart rate"}}})

title("5. multi_match: search several fields, boost 'name' x3 (^3)")
search({"query": {"multi_match": {"query": "coffee", "fields": ["name^3", "description"]}}})

title("6. Typo tolerance with fuzziness ('headphnes', 'keybord')")
search({"query": {"match": {"name": {"query": "headphnes keybord", "fuzziness": "AUTO"}}}})

title("7. term on a keyword field: exact match, NO analysis")
search({"query": {"term": {"category": "kitchen"}}})
note("Classic beginner trap: 'term' on a TEXT field. 'Espresso Machine' was")
note("indexed as tokens [espresso, machin], so this finds nothing:")
search({"query": {"term": {"name": "Espresso Machine"}}})
note("...but the keyword sub-field name.raw holds the exact string:")
search({"query": {"term": {"name.raw": "Espresso Machine"}}})

title("8. range on numbers and dates")
search({"query": {"range": {"price": {"gte": 100, "lte": 200}}}})
search({"query": {"range": {"created_at": {"gte": "2025-05-01"}}}}, ("name", "created_at"))

title("9. bool: combine everything (the query you'll write most at work)")
note("'running' in text (scored) + in stock + price < 200 (filters) + not brand Pulse")
search({
    "query": {
        "bool": {
            "must": [{"multi_match": {"query": "running", "fields": ["name^2", "description", "tags"]}}],
            "filter": [
                {"term": {"in_stock": True}},
                {"range": {"price": {"lt": 200}}},
            ],
            "must_not": [{"term": {"brand": "Pulse"}}],
            "should": [{"range": {"rating": {"gte": 4.5}}}],  # bonus score if true
        }
    }
}, ("name", "brand", "price", "rating"))

title("10. Sorting, pagination (from/size) and choosing returned fields")
search({
    "query": {"term": {"category": "computers"}},
    "sort": [{"price": "desc"}],
    "from": 0,
    "size": 3,
    "_source": ["name", "price", "category"],
})
note("When you sort by a field, _score isn't computed (shows n/a).")
note("For deep pagination (> 10,000 results) use search_after instead of from/size.")
