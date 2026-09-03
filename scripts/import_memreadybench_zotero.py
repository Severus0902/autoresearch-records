# -*- coding: utf-8 -*-
"""Import MemReadyBench collision-audit papers into Zotero's Memory collection.

Zotero 9 exposes a read-only local Web API but accepts translated items through
the Connector HTTP server. The script is idempotent by normalized title and
requires the Memory collection to be selected in Zotero.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import uuid
from urllib.request import Request, urlopen


BASE = "http://127.0.0.1:23119"
COLLECTION_KEY = "XQRQDC4S"
COLLECTION_NAME = "Memory"


PAPERS = [
    ("2608.04289", "2026-08-04", "SafeCommit: Certifying When Memory-Grounded Agents May Safely Act", "P0"),
    ("2608.19564", "2026-08-20", "Remember, Verify, or Ask? Cross-Family Evaluation of Memory Commitment in LLM Agents", "P0"),
    ("2607.10059", "2026-07-11", "AgentAbstain: Do LLM Agents Know When Not to Act?", "P0"),
    ("2608.01285", "2026-08-02", "Stop When Memory Suffices: Evidence-Conditioned Progressive Execution for LLM Agents", "P0"),
    ("2602.02704", "2026-02-02", "InfMem: Learning System-2 Memory Control for Long-Context Agent", "P0"),
    ("2607.01071", "2026-07-01", "MemSyco-Bench: Benchmarking Sycophancy in Agent Memory", "P0"),
    ("2605.03534", "2026-05-05", "SURE-RAG: Sufficiency and Uncertainty-Aware Evidence Verification for Selective Retrieval-Augmented Generation", "P1"),
    ("2604.00131", "2026-03-31", "Oblivion: Self-Adaptive Agentic Memory Control through Decay-Driven Activation", "P1"),
    ("2604.27283", "2026-04-30", "Learning When to Remember: Risk-Sensitive Contextual Bandits for Abstention-Aware Memory Retrieval in LLM-Based Coding Agents", "P1"),
    ("2604.08455", "2026-04-09", "KnowU-Bench: Towards Interactive, Proactive, and Personalized Mobile Agent Evaluation", "P1"),
    ("2605.09252", "2026-05-10", "LLM Agents Already Know When to Call Tools -- Even Without Reasoning", "P1"),
    ("2602.16699", "2026-02-18", "Calibrate-Then-Act: Cost-Aware Exploration in LLM Agents", "P1"),
    ("2511.08798", "2025-11-11", "Structured Uncertainty guided Clarification for LLM Agents", "P1"),
    ("2601.15703", "2026-01-22", "Agentic Uncertainty Quantification", "P2"),
    ("2606.18037", "2026-06-18", "ProvenanceGuard: Source-Aware Factuality Verification for MCP-Based LLM Agents", "P2"),
    ("2602.11182", "2026-01-27", "MetaMem: Evolving Meta-Memory for Knowledge Utilization through Self-Reflective Symbolic Optimization", "P2"),
]


def normalize_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def request_json(path: str, payload=None):
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Accept": "application/json", "User-Agent": "autoresearch-zotero-import/1.0"}
    if body is not None:
        headers["Content-Type"] = "application/json"
        headers["Zotero-Allowed-Request"] = "true"
    req = Request(BASE + path, data=body, headers=headers, method="POST" if body is not None else "GET")
    with urlopen(req, timeout=30) as response:
        raw = response.read()
        return response.status, json.loads(raw.decode("utf-8")) if raw else None


def zotero_item(arxiv_id: str, date: str, title: str, priority: str):
    url = f"https://arxiv.org/abs/{arxiv_id}"
    return {
        "id": f"memreadybench-{arxiv_id.replace('.', '-')}",
        "itemType": "journalArticle",
        "title": title,
        "creators": [],
        "abstractNote": "",
        "publicationTitle": "arXiv",
        "date": date,
        "language": "English",
        "DOI": f"10.48550/arXiv.{arxiv_id}",
        "url": url,
        "accessDate": "2026-09-03",
        "archive": "arXiv",
        "archiveLocation": arxiv_id,
        "libraryCatalog": "arXiv.org",
        "extra": f"arXiv: {arxiv_id}",
        "tags": [
            {"tag": priority, "type": 1},
            {"tag": "agentic-memory", "type": 1},
            {"tag": "MemReadyBench-related", "type": 1},
            {"tag": "frontier-collision", "type": 1},
            {"tag": "source-aware-readiness", "type": 1},
        ],
        "seeAlso": [],
        "attachments": [],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Create missing records in Zotero")
    args = parser.parse_args()

    _, selected = request_json("/connector/getSelectedCollection", {})
    if selected.get("name") != COLLECTION_NAME or str(selected.get("id")) != "11":
        raise SystemExit(
            f"Refusing to import: selected Zotero target is {selected.get('name')!r} "
            f"(id={selected.get('id')}), expected Memory (id=11)."
        )

    _, current = request_json(
        f"/api/users/0/collections/{COLLECTION_KEY}/items/top?limit=100&format=json"
    )
    existing = {
        normalize_title(entry.get("data", {}).get("title", ""))
        for entry in current
        if entry.get("data", {}).get("title")
    }
    missing = [paper for paper in PAPERS if normalize_title(paper[2]) not in existing]

    print(f"selected={selected['name']} existing={len(existing)} missing={len(missing)}")
    for arxiv_id, _, title, priority in missing:
        print(f"  {priority} {arxiv_id} {title}")

    if not args.apply or not missing:
        return

    payload = {
        "items": [zotero_item(*paper) for paper in missing],
        "uri": "https://arxiv.org/",
        "sessionID": f"memreadybench-{uuid.uuid4().hex}",
    }
    status, _ = request_json("/connector/saveItems", payload)
    if status != 201:
        raise SystemExit(f"Unexpected Zotero Connector response: HTTP {status}")

    time.sleep(3)
    _, updated = request_json(
        f"/api/users/0/collections/{COLLECTION_KEY}/items/top?limit=100&format=json"
    )
    by_title = {
        normalize_title(entry.get("data", {}).get("title", "")): entry.get("key")
        for entry in updated
        if entry.get("data", {}).get("title")
    }
    print("imported:")
    for _, _, title, _ in missing:
        print(f"  {by_title.get(normalize_title(title), 'NOT_FOUND')} {title}")


if __name__ == "__main__":
    main()
