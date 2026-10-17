#!/usr/bin/env python3
"""Copy the API contract from a GoWave checkout into public/api/openapi.json.

Usage: python3 scripts/sync_openapi.py [path/to/gowave]
"""
import json
import os
import sys

repo = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/GoWave")
source = os.path.join(repo, "backend-go/internal/contracts/openapi.json")
target = os.path.join(os.path.dirname(__file__), "..", "public/api/openapi.json")

spec = json.load(open(source, encoding="utf-8"))
contract = spec.get("info", {}).get("version", "")
spec["info"]["title"] = "GoWave API"
spec["info"]["description"] = (
    f"GoWave implements the Remnawave backend API, contract `@remnawave/backend-contract` {contract}. "
    "Requests go to your panel: `https://<panel domain>/api/...` with `Authorization: Bearer <token>`."
)
json.dump(spec, open(target, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"wrote {os.path.normpath(target)} (contract {contract}, {len(spec.get('paths', {}))} paths)")
