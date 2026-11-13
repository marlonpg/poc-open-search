# OpenSearch POC: learn by running it

A hands-on playground for learning [OpenSearch](https://opensearch.org): a local cluster in Docker, a small product catalog, and 7 short lessons. Each lesson prints the exact HTTP requests it sends and what comes back.

## 1. What is OpenSearch, in one minute

OpenSearch is a **search and analytics engine**. It's the open-source fork of Elasticsearch 7.10, maintained by AWS and the Linux Foundation. Almost everything you read about Elasticsearch 7.x applies here too.

You send it JSON documents. It indexes them so that you can:

- **search text** quickly, with relevance ranking, typo tolerance and highlighting (search boxes, product catalogs);
- **filter and aggregate** large amounts of data (dashboards, log analytics, metrics);
- do vector / semantic search (k-NN plugin). That's out of scope here.

Everything happens through a **REST API** on port `9200`. Any language works; client libraries are thin wrappers over that API.

### Mental model (SQL comparison)

| OpenSearch | Relational DB | Notes |
|---|---|---|
| Cluster | Database server | One or more nodes |
| Node | Server process | We run 1 |
| **Index** | Table | Named collection of documents |
| **Document** | Row | A JSON object with an `_id` |
| Field | Column | |
| **Mapping** | Schema | Field types and how text is analyzed |
| Shard / replica | Partition / copy | How an index is split and duplicated across nodes |
| Query DSL | `SELECT … WHERE` | JSON query language (SQL and PPL plugins also exist) |
| Aggregation | `GROUP BY` / `AVG()` | |

### Why search is fast: the inverted index

When a `text` field is indexed, an **analyzer** breaks it into tokens: `"Running Shoes"` becomes `[run, shoe]`. Then OpenSearch stores a map of *token → documents containing it*, like the index at the back of a book. A query is analyzed the same way and looked up in that map. Most "why doesn't my search match?" questions come down to analyzers, so lesson 2 shows them with the `_analyze` API.

### The two field types you must understand

- **`text`**: analyzed into tokens. Use it for full-text search (`match`). You can't sort or aggregate on it.
- **`keyword`**: stored as one exact value. Use it for filters (`term`), sorting, aggregations, IDs and tags.

A field can have both: `name` (text) plus `name.raw` (keyword).

## 2. Run it

Requirements: Docker Desktop and Python 3.10+.

```bash
docker compose up -d
```

Wait about 30–60 s, then check it's up:

```bash
curl http://localhost:9200/_cluster/health
```

- REST API: http://localhost:9200
- OpenSearch Dashboards (web UI): http://localhost:5601. Use **Dev Tools** to type queries by hand, as shown in [devtools.md](devtools.md).

Install the dependency:

```bash
pip install -r requirements.txt
```

Then run the lessons in order:

```bash
cd lessons
python 01_cluster_basics.py
python 02_create_index.py
python 03_index_documents.py
python 04_search_basics.py
python 05_aggregations.py
python 06_relevance.py
python 07_update_delete_aliases.py
```

Or run them all at once with `python run_all.py`. Each lesson is safe to re-run, because lesson 2 recreates the index.

## 3. The lessons

| # | File | You'll learn |
|---|---|---|
| 1 | [01_cluster_basics.py](lessons/01_cluster_basics.py) | Cluster health (green/yellow/red), nodes, `_cat` APIs |
| 2 | [02_create_index.py](lessons/02_create_index.py) | Settings, **mappings**, `text` vs `keyword`, custom analyzer, `_analyze` |
| 3 | [03_index_documents.py](lessons/03_index_documents.py) | Index/get by id, strict mapping, **`_bulk`**, near-real-time refresh |
| 4 | [04_search_basics.py](lessons/04_search_basics.py) | `match`, `match_phrase`, `multi_match`, fuzziness, `term`, `range`, **`bool`** (must/filter/should/must_not), sort and paging |
| 5 | [05_aggregations.py](lessons/05_aggregations.py) | `terms`, `stats`, `cardinality`, sub-aggs, `range`, `date_histogram`, facets |
| 6 | [06_relevance.py](lessons/06_relevance.py) | BM25 scoring, highlighting, `explain`, boosting, `function_score` |
| 7 | [07_update_delete_aliases.py](lessons/07_update_delete_aliases.py) | Partial and scripted updates, update/delete by query, **reindex + alias switch** |

The sample data is [data/products.json](data/products.json): 25 fake products.

## 4. Things that usually trip people up

1. **`term` query on a `text` field finds nothing.** The stored tokens are lowercased and stemmed, but `term` isn't analyzed. Use `match` for text, and `term` on keyword fields.
2. **"I indexed a doc but search doesn't see it."** Search is *near*-real-time; new documents appear after the next refresh (about 1 s).
3. **You can't change a field's type** once data is indexed. Create a new index, `_reindex`, and switch an alias. Applications should always talk to an alias.
4. **Yellow health on a single node** is normal if replicas > 0, because a replica can't live on the same node as its primary.
5. **Put non-scoring conditions in `filter`, not `must`.** Filters are faster and cached.
6. **`from + size` is capped at 10,000.** Use `search_after` for deep paging.
7. **Dynamic mapping guesses types.** That's fine for exploring, but define explicit mappings in production.

## 5. Cleanup

Stop the containers:

```bash
docker compose down
```

Stop them and delete the data volume:

```bash
docker compose down -v
```

> ⚠️ This setup disables the security plugin (no TLS, no auth) to keep things simple. Real clusters, including the one at work, will need HTTPS plus a username and password or IAM.

## Next steps to explore

- Use the official client for your language, for example `opensearch-py` or `@opensearch-project/opensearch`.
- Explore **Discover** and **Visualize** in Dashboards with an index pattern on `products`.
- Try the SQL and PPL plugins (examples in [devtools.md](devtools.md)).
- Look into **Index templates** and **ISM (Index State Management)** for time-based log indices.
- Try **k-NN / neural search** for vector and semantic search.
