from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any, Dict, List

from .schemas import Triple


def _fb_mid(mid: str) -> str:
    return mid.strip().lstrip("/")


def _strip_ns(value: str) -> str:
    prefix = "http://rdf.freebase.com/ns/"
    if value.startswith(prefix):
        return value[len(prefix) :]
    return value


class FreebaseAdapter:
    def __init__(self, endpoint: str, timeout_sec: int = 30, enabled: bool = True):
        self.endpoint = endpoint
        self.timeout_sec = timeout_sec
        self.enabled = enabled

    def check(self) -> Dict[str, Any]:
        if not self.enabled:
            return {"ok": False, "reason": "kg.enabled=false"}
        try:
            self.query("ASK { ?s ?p ?o }", accept="application/sparql-results+json")
            return {"ok": True, "endpoint": self.endpoint}
        except Exception as exc:  # pragma: no cover - depends on remote endpoint
            return {"ok": False, "endpoint": self.endpoint, "reason": str(exc)}

    def query(self, sparql: str, accept: str = "application/sparql-results+json") -> Dict[str, Any]:
        params = urllib.parse.urlencode({"query": sparql, "format": "json"})
        url = f"{self.endpoint}?{params}"
        request = urllib.request.Request(url, headers={"Accept": accept})
        with urllib.request.urlopen(request, timeout=self.timeout_sec) as response:
            payload = response.read().decode("utf-8")
        return json.loads(payload)

    def get_out_edges(self, mid: str, limit: int = 100) -> List[Triple]:
        if not self.enabled:
            return []
        mid = _fb_mid(mid)
        sparql = f"""
PREFIX ns: <http://rdf.freebase.com/ns/>
SELECT ?r ?o WHERE {{
  ns:{mid} ?r ?o .
  FILTER(STRSTARTS(STR(?r), STR(ns:)))
}} LIMIT {int(limit)}
"""
        return self._parse_edges(mid, self.query(sparql), direction="out")

    def get_in_edges(self, mid: str, limit: int = 100) -> List[Triple]:
        if not self.enabled:
            return []
        mid = _fb_mid(mid)
        sparql = f"""
PREFIX ns: <http://rdf.freebase.com/ns/>
SELECT ?s ?r WHERE {{
  ?s ?r ns:{mid} .
  FILTER(STRSTARTS(STR(?r), STR(ns:)))
}} LIMIT {int(limit)}
"""
        return self._parse_edges(mid, self.query(sparql), direction="in")

    def get_names(self, mid: str, limit: int = 5) -> List[str]:
        if not self.enabled:
            return []
        mid = _fb_mid(mid)
        sparql = f"""
PREFIX ns: <http://rdf.freebase.com/ns/>
SELECT ?name WHERE {{
  ns:{mid} ns:type.object.name ?name .
}} LIMIT {int(limit)}
"""
        data = self.query(sparql)
        names = []
        for row in data.get("results", {}).get("bindings", []):
            value = row.get("name", {}).get("value", "")
            if value:
                names.append(value)
        return names

    def _parse_edges(self, pivot_mid: str, data: Dict[str, Any], direction: str) -> List[Triple]:
        edges: List[Triple] = []
        for row in data.get("results", {}).get("bindings", []):
            relation = _strip_ns(row.get("r", {}).get("value", ""))
            if direction == "out":
                target = _strip_ns(row.get("o", {}).get("value", ""))
                edges.append(Triple(source=pivot_mid, relation=relation, target=target, direction="out"))
            else:
                source = _strip_ns(row.get("s", {}).get("value", ""))
                edges.append(Triple(source=source, relation=relation, target=pivot_mid, direction="in"))
        return edges
