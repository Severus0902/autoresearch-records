from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


def experiment_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_config(path: str | Path) -> Dict[str, Any]:
    cfg_path = Path(path)
    if not cfg_path.is_absolute():
        cfg_path = experiment_root() / cfg_path
    with cfg_path.open("r", encoding="utf-8-sig") as f:
        cfg = json.load(f)
    cfg["_config_path"] = str(cfg_path)
    return cfg


def output_root(cfg: Dict[str, Any]) -> Path:
    root = Path(os.path.expandvars(cfg["project"]["output_root"])).expanduser()
    return root


def resolve_output_path(cfg: Dict[str, Any], key: str) -> Path:
    value = cfg["outputs"][key]
    path = Path(os.path.expandvars(value)).expanduser()
    if path.is_absolute():
        return path
    return output_root(cfg) / path


def resolve_dataset_path(cfg: Dict[str, Any]) -> Path:
    return Path(os.path.expandvars(cfg["dataset"]["path"])).expanduser()


def assert_remote_safety(cfg: Dict[str, Any]) -> None:
    safety = cfg.get("remote_safety", {})
    allowed_root = safety.get("allowed_root")
    if not allowed_root:
        return
    allowed = Path(allowed_root).expanduser()
    root = output_root(cfg)
    try:
        root.relative_to(allowed)
    except ValueError as exc:
        raise ValueError(f"output_root must stay under {allowed}: {root}") from exc
    if safety.get("allow_delete", False):
        raise ValueError("allow_delete must stay false for this experiment framework.")


def ensure_output_dirs(cfg: Dict[str, Any]) -> None:
    assert_remote_safety(cfg)
    root = output_root(cfg)
    for rel in ("cache", "outputs", "outputs/memory", "outputs/eval", "logs", "runs"):
        (root / rel).mkdir(parents=True, exist_ok=True)
