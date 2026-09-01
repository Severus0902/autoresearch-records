from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from idea1_kgr.config import ensure_output_dirs, load_config, resolve_dataset_path, resolve_output_path
from idea1_kgr.data_adapters import load_samples
from idea1_kgr.freebase_adapter import FreebaseAdapter
from idea1_kgr.io_utils import write_jsonl
from idea1_kgr.subgraph_builder import SubgraphBuilder


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
        offset=int(cfg["dataset"].get("offset", 0)),
    )
    kg_cfg = cfg.get("kg", {})
    kg = FreebaseAdapter(
        endpoint=kg_cfg.get("sparql_endpoint", ""),
        timeout_sec=int(kg_cfg.get("timeout_sec", 30)),
        enabled=bool(kg_cfg.get("enabled", True)),
    )
    sg_cfg = cfg.get("subgraph", {})
    builder = SubgraphBuilder(
        kg=kg,
        max_hops=int(sg_cfg.get("max_hops", 2)),
        max_nodes=int(sg_cfg.get("max_nodes", 200)),
        max_edges=int(sg_cfg.get("max_edges", 500)),
        edge_limit_per_entity=int(kg_cfg.get("edge_limit_per_entity", 80)),
        max_relation_candidates=int(sg_cfg.get("max_relation_candidates", 30)),
    )
    records = [builder.build(sample).to_dict() for sample in samples]
    count = write_jsonl(resolve_output_path(cfg, "subgraphs"), records, overwrite=args.overwrite)
    print(f"wrote_subgraphs={count}")
    if records:
        avg_actions = sum(len(row["candidate_actions"]) for row in records) / len(records)
        print(f"avg_candidate_actions={avg_actions:.2f}")


if __name__ == "__main__":
    main()
