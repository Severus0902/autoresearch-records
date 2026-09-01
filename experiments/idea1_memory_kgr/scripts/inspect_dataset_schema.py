from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from idea1_kgr.data_adapters import load_samples


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["webqsp", "cwq"], required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    with open(args.path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    print(f"raw_type={type(data).__name__}")
    print(f"raw_len={len(data) if hasattr(data, '__len__') else 'unknown'}")

    records = data if isinstance(data, list) else data.get("data", [])
    for idx in range(args.offset, min(args.offset + args.limit, len(records))):
        record = records[idx]
        print(f"raw_idx={idx}")
        print(f"raw_keys={sorted(record.keys())}")
        preview = {key: record.get(key) for key in sorted(record.keys())[:20]}
        print(json.dumps(preview, ensure_ascii=False)[:1000])

    samples = load_samples(
        args.dataset,
        args.path,
        offset=args.offset,
        limit=args.limit,
        split="inspect",
    )
    print(f"adapter_loaded={len(samples)}")
    for sample in samples:
        print(
            json.dumps(
                {
                    "qid": sample.qid,
                    "question": sample.question,
                    "topic_entities": [entity.__dict__ for entity in sample.topic_entities],
                    "gold_answers": [answer.__dict__ for answer in sample.gold_answers],
                    "gold_relation_chain": sample.gold_relation_chain,
                },
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()
