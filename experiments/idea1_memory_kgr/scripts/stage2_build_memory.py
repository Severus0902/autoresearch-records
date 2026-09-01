from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from idea1_kgr.config import ensure_output_dirs, load_config, resolve_dataset_path, resolve_output_path
from idea1_kgr.data_adapters import load_samples
from idea1_kgr.memory_store import build_memory_from_samples


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/webqsp_pilot.json")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    cfg = load_config(args.config)
    ensure_output_dirs(cfg)
    samples = load_samples(
        dataset=cfg["dataset"]["name"],
        path=resolve_dataset_path(cfg),
        limit=int(cfg["dataset"].get("limit", 0)),
        split=cfg["dataset"].get("split", "unknown"),
    )
    store = build_memory_from_samples(samples)
    count = store.save(resolve_output_path(cfg, "memory"), overwrite=args.overwrite)
    print(f"wrote_memory_items={count}")


if __name__ == "__main__":
    main()
