from __future__ import annotations

import argparse
import platform
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from idea1_kgr.config import ensure_output_dirs, load_config, output_root, resolve_dataset_path
from idea1_kgr.freebase_adapter import FreebaseAdapter


def existing_parent(path: Path) -> Path:
    current = path
    while not current.exists() and current != current.parent:
        current = current.parent
    return current


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/webqsp_pilot.json")
    parser.add_argument("--make-dirs", action="store_true", help="Create framework output dirs.")
    args = parser.parse_args()

    cfg = load_config(args.config)
    dataset_path = resolve_dataset_path(cfg)
    root = output_root(cfg)

    print("== Idea1 KGR inventory ==")
    print(f"python={platform.python_version()}")
    print(f"platform={platform.platform()}")
    print(f"config={cfg['_config_path']}")
    print(f"dataset={cfg['dataset']['name']} path={dataset_path} exists={dataset_path.exists()}")
    print(f"output_root={root}")

    allowed = cfg.get("remote_safety", {}).get("allowed_root", "")
    print(f"allowed_root={allowed}")
    print(f"allow_delete={cfg.get('remote_safety', {}).get('allow_delete')}")

    usage = shutil.disk_usage(str(existing_parent(root)))
    print(f"disk_total_gb={usage.total / 1024**3:.1f}")
    print(f"disk_free_gb={usage.free / 1024**3:.1f}")

    if args.make_dirs:
        ensure_output_dirs(cfg)
        print("output_dirs=created")
    else:
        print("output_dirs=not_created")

    kg_cfg = cfg.get("kg", {})
    kg = FreebaseAdapter(
        endpoint=kg_cfg.get("sparql_endpoint", ""),
        timeout_sec=int(kg_cfg.get("timeout_sec", 30)),
        enabled=bool(kg_cfg.get("enabled", True)),
    )
    print(f"kg_check={kg.check()}")


if __name__ == "__main__":
    main()
