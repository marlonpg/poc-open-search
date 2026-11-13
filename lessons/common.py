"""Tiny helper shared by all lessons.

OpenSearch is "just" a REST API that speaks JSON. Every call in these lessons
goes through `call()`, which prints the request in the same format you would
type in OpenSearch Dashboards -> Dev Tools, then prints the response.
"""
import json
import os
import sys

import requests

BASE_URL = os.environ.get("OPENSEARCH_URL", "http://localhost:9200")
INDEX = "products"

# Make Windows consoles print UTF-8 and colors nicely.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
CYAN, YELLOW, GREEN, DIM, RESET = "\033[36m", "\033[33m", "\033[32m", "\033[2m", "\033[0m"


def title(text: str) -> None:
    print(f"\n{YELLOW}{'=' * 70}\n{text}\n{'=' * 70}{RESET}")


def note(text: str) -> None:
    print(f"{DIM}# {text}{RESET}")


def call(method: str, path: str, body=None, show_response=True, ndjson: str | None = None):
    """Send a request to OpenSearch and pretty-print both sides."""
    print(f"\n{CYAN}{method} {path}{RESET}")
    if body is not None:
        print(json.dumps(body, indent=2, ensure_ascii=False))
    elif ndjson is not None:
        lines = ndjson.strip().splitlines()
        print("\n".join(lines[:4]) + (f"\n... ({len(lines)} lines total)" if len(lines) > 4 else ""))

    headers = {"Content-Type": "application/x-ndjson" if ndjson else "application/json"}
    resp = requests.request(
        method,
        BASE_URL + path,
        headers=headers,
        data=ndjson if ndjson else (json.dumps(body) if body is not None else None),
        timeout=30,
    )
    try:
        data = resp.json()
    except ValueError:
        data = resp.text

    if show_response:
        print(f"{GREEN}-> {resp.status_code}{RESET}")
        print(json.dumps(data, indent=2, ensure_ascii=False) if not isinstance(data, str) else data)
    return data


def print_hits(result: dict, fields=("name", "category", "price")) -> None:
    """Compact view of search results: score + a few fields."""
    hits = result.get("hits", {})
    total = hits.get("total", {}).get("value")
    print(f"{GREEN}-> {total} hit(s){RESET}")
    for h in hits.get("hits", []):
        src = h.get("_source", {})
        score = h.get("_score")
        score_txt = f"{score:6.3f}" if isinstance(score, (int, float)) else "  n/a "
        values = " | ".join(str(src.get(f)) for f in fields)
        print(f"  score={score_txt}  id={h['_id']:<4} {values}")
        if "highlight" in h:
            for field, frags in h["highlight"].items():
                print(f"      highlight[{field}]: {frags}")
