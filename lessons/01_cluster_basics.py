"""Lesson 1 - Is it alive? Cluster, nodes and indices.

Vocabulary:
  cluster -> one or more OpenSearch servers (nodes) working together
  node    -> a single OpenSearch process (we run exactly 1 in docker)
  index   -> a named collection of JSON documents (~ a table in SQL)
  shard   -> an index is split into shards so it can spread over nodes
  replica -> a copy of a shard on ANOTHER node, for safety and read speed
"""
from common import call, note, title

title("1. Who are you? (basic info / version)")
call("GET", "/")

title("2. Cluster health")
note("green = all shards OK; yellow = primaries OK but some replicas unassigned;")
note("red = some primary shard missing. With 1 node, indices with replicas are yellow.")
call("GET", "/_cluster/health")

title("3. Nodes in the cluster (the _cat APIs are human-friendly tables)")
call("GET", "/_cat/nodes?v")

title("4. Which indices exist right now?")
note("Names starting with '.' are system indices (e.g. used by Dashboards).")
call("GET", "/_cat/indices?v&expand_wildcards=all")
