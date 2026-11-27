#!/usr/bin/env python3
"""Sync graph metadata while preserving the calibrated inputs in risk_data.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    graph, _ = json.JSONDecoder().raw_decode(html.split("const DATA = ", 1)[1])
    path = ROOT / "risk_data.json"
    risk = json.loads(path.read_text(encoding="utf-8"))
    for node in graph["nodes"]:
        entry = risk["nodes"].setdefault(node["key"], {
            "substitution": 0.5,
            "inventory_weeks": risk["default_buffer"],
            "uses_defaults": True,
        })
        for field in ("name", "tier", "country"):
            entry[field] = node[field]
        entry["usd_b"] = node.get("usd")
    path.write_text(json.dumps(risk, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
