"""Lesson 3 - Putting documents in (indexing) and getting them back.

  PUT  /index/_doc/<id>   -> create or REPLACE the document with that id
  POST /index/_doc        -> create with an auto-generated id
  GET  /index/_doc/<id>   -> fetch one document by id (real-time, no search)
  POST /_bulk             -> many operations in ONE request (use this for volume!)

Near-real-time: a newly indexed document becomes visible to SEARCH after the
next "refresh" (default every 1s). GET by id works immediately. In lessons
we pass ?refresh=true / call _refresh so results show up right away.
"""
import json
from pathlib import Path

from common import INDEX, call, note, title

products = json.loads((Path(__file__).parent.parent / "data" / "products.json").read_text(encoding="utf-8"))

title("1. Index ONE document with an explicit id")
first = dict(products[0])
doc_id = first.pop("id")
call("PUT", f"/{INDEX}/_doc/{doc_id}", first)
note("Look at 'result': 'created'. Run it again and it becomes 'updated' with _version 2.")

title("2. Get it back by id")
call("GET", f"/{INDEX}/_doc/{doc_id}")

title("3. Strict mapping in action: unknown field is rejected")
call("PUT", f"/{INDEX}/_doc/999", {"name": "Bad doc", "colour": "red"})

title("4. Bulk-index the rest of the catalog")
note("_bulk body is NDJSON: an action line, then the document line, repeated.")
lines = []
for p in products[1:]:
    p = dict(p)
    lines.append(json.dumps({"index": {"_index": INDEX, "_id": p.pop("id")}}))
    lines.append(json.dumps(p))
ndjson = "\n".join(lines) + "\n"  # bulk body MUST end with a newline
result = call("POST", "/_bulk?refresh=true", ndjson=ndjson, show_response=False)
print(f"-> errors={result['errors']}, items={len(result['items'])}, took={result['took']}ms")

title("5. Count documents")
call("GET", f"/{INDEX}/_count")

title("6. Fetch several by id at once (_mget)")
call("POST", f"/{INDEX}/_mget", {"ids": ["2", "13", "22"]})
