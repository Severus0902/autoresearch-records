import copy
import json
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_CONFIG = ROOT / "config.example.json"
LOCAL_CONFIG = ROOT / "config.local.json"


DEFAULT_CONFIG: Dict[str, Any] = {
    "project": {
        "name": "autoresearch",
        "timezone": "Asia/Hong_Kong",
    },
    "zotero": {
        "base_url": "http://127.0.0.1:23119/api",
        "library": "users/0",
        "page_size": 100,
    },
    "markdown": {
        "root": "docs",
        "idea_dir": "docs/ideas",
        "experiment_dir": "docs/experiments",
        "result_dir": "docs/results",
    },
    "git": {
        "remote": "origin",
        "branch": "main",
        "auto_push": True,
    },
    "server": {
        "ssh_target": "",
        "remote_workdir": "",
        "ssh_options": [],
    },
}


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_config() -> Dict[str, Any]:
    config = copy.deepcopy(DEFAULT_CONFIG)
    if EXAMPLE_CONFIG.exists():
        config = deep_merge(config, read_json(EXAMPLE_CONFIG))
    if LOCAL_CONFIG.exists():
        config = deep_merge(config, read_json(LOCAL_CONFIG))
    return config


def project_path(*parts: str) -> Path:
    return ROOT.joinpath(*parts)

