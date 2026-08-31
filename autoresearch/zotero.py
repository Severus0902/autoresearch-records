import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


def _request_json(url: str) -> Tuple[Any, Dict[str, str]]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "AutoResearch/0.1",
        },
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))
        headers = {key: value for key, value in response.headers.items()}
    return payload, headers


def api_url(base_url: str, path: str, params: Dict[str, Any]) -> str:
    base = base_url.rstrip("/")
    clean_path = path.strip("/")
    query = urllib.parse.urlencode(params)
    return f"{base}/{clean_path}?{query}"


def ping(config: Dict[str, Any]) -> Dict[str, Any]:
    zotero = config["zotero"]
    url = api_url(
        zotero["base_url"],
        f"{zotero['library']}/items/top",
        {"limit": 1, "format": "json"},
    )
    payload, headers = _request_json(url)
    library = {}
    if payload:
        library = payload[0].get("library", {})
    return {
        "ok": True,
        "version": headers.get("X-Zotero-Version"),
        "api_version": headers.get("Zotero-API-Version"),
        "schema_version": headers.get("Zotero-Schema-Version"),
        "total_results": int(headers.get("Total-Results", "0")),
        "library": library,
    }


def fetch_top_items(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    zotero = config["zotero"]
    page_size = int(zotero.get("page_size", 100))
    start = 0
    items: List[Dict[str, Any]] = []

    while True:
        url = api_url(
            zotero["base_url"],
            f"{zotero['library']}/items/top",
            {
                "limit": page_size,
                "start": start,
                "format": "json",
            },
        )
        payload, _headers = _request_json(url)
        if not payload:
            break
        items.extend(payload)
        if len(payload) < page_size:
            break
        start += page_size

    return items


def item_summary(item: Dict[str, Any]) -> Dict[str, Any]:
    data = item.get("data", {})
    creators = data.get("creators", [])
    authors = [
        " ".join(
            part
            for part in [
                creator.get("firstName", ""),
                creator.get("lastName", ""),
            ]
            if part
        )
        for creator in creators
        if creator.get("creatorType") == "author"
    ]
    return {
        "key": data.get("key") or item.get("key"),
        "citationKey": data.get("citationKey", ""),
        "itemType": data.get("itemType", ""),
        "title": data.get("title", ""),
        "date": data.get("date", ""),
        "year": item.get("meta", {}).get("parsedDate", ""),
        "authors": authors,
        "DOI": data.get("DOI", ""),
        "url": data.get("url", ""),
        "collections": data.get("collections", []),
        "tags": [tag.get("tag") for tag in data.get("tags", []) if tag.get("tag")],
        "dateModified": data.get("dateModified", ""),
    }


def write_sync_outputs(items: Iterable[Dict[str, Any]], output_dir: Path) -> Dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summaries = [item_summary(item) for item in items]
    json_path = output_dir / "items.json"
    md_path = output_dir / "library.md"

    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(summaries, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    lines = ["# Zotero Library", ""]
    for item in summaries:
        title = item["title"] or "(untitled)"
        cite = item["citationKey"] or item["key"]
        year = item["year"] or item["date"]
        authors = ", ".join(item["authors"][:3])
        suffix = f" ({year})" if year else ""
        lines.append(f"- `@{cite}` {title}{suffix}")
        if authors:
            lines.append(f"  Authors: {authors}")
        if item["DOI"]:
            lines.append(f"  DOI: {item['DOI']}")
        if item["url"]:
            lines.append(f"  URL: {item['url']}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {"json": json_path, "markdown": md_path}


def sync(config: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    try:
        items = fetch_top_items(config)
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Could not reach Zotero Local API. Keep Zotero Desktop open and use "
            "http://127.0.0.1:23119/api in config."
        ) from exc
    paths = write_sync_outputs(items, output_dir)
    return {"count": len(items), "paths": paths}


def citation_keys_from_text(text: str) -> List[str]:
    keys = re.findall(r"(?<![\w.-])@([A-Za-z0-9_:.#-]+)", text)
    return sorted(set(keys))

