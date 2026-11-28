"""Runs inside the kb pod: real searches against its own server, printed with timings."""

import json
import time
import urllib.error
import urllib.request


def call(method, path, body=None):
    request = urllib.request.Request("http://127.0.0.1:8000" + path, method=method,
                                     data=None if body is None else json.dumps(body).encode())
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            status, answer = response.status, json.load(response)
    except urllib.error.HTTPError as error:
        status, answer = error.code, json.load(error)
    return status, answer, time.monotonic() - started


status, answer, seconds = call("GET", "/coverage")
print(f"GET /coverage -> {status} in {seconds:.1f}s\n{json.dumps(answer)}")
for body in ({"query": "tool that helps students plan study time"},
             {"query": "tool that helps students plan study time", "filters": {"source": "hackernews"}},
             {"query": "find broken links", "filters": {"date_from": "2025-01-01", "date_to": "2025-12-31"}},
             {"query": "habit tracker", "filters": {"niche": "productivity"}},
             {"query": "habit tracker", "filters": {"source": "producthunt"}},
             {"query": "x", "filters": {"date_from": "soon"}}):
    status, answer, seconds = call("POST", "/search", body)
    print(f"\nPOST /search {json.dumps(body)} -> {status} in {seconds:.1f}s")
    if status != 200:
        print(json.dumps(answer))
        continue
    print(f"{len(answer)} items")
    for item in answer[:4]:
        print(f"  {item['evidence_id']}  {item['source']}  {item['url']}")
        print(f"    {item['quote'][:110]}")
