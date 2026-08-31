import json
import re
from pathlib import Path
from typing import Any, Dict, List

from .zotero import citation_keys_from_text


def parse_frontmatter(text: str) -> Dict[str, Any]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}

    metadata: Dict[str, Any] = {}
    for raw_line in text[4:end].splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"')
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            metadata[key] = [
                item.strip().strip('"').strip("'")
                for item in inner.split(",")
                if item.strip()
            ]
        else:
            metadata[key] = value
    return metadata


def first_heading(text: str) -> str:
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def index_markdown(root: Path) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for path in sorted(root.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        metadata = parse_frontmatter(text)
        entries.append(
            {
                "path": str(path),
                "title": metadata.get("title") or first_heading(text) or path.stem,
                "type": metadata.get("type", ""),
                "status": metadata.get("status", ""),
                "zotero": metadata.get("zotero", []),
                "citation_keys": citation_keys_from_text(text),
                "tags": metadata.get("tags", []),
            }
        )
    return entries


def write_index(root: Path, output_path: Path) -> Dict[str, Any]:
    entries = index_markdown(root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(entries, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return {"count": len(entries), "path": output_path}

