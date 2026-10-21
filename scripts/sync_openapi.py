#!/usr/bin/env python3
"""Copy the API contract from a GoWave checkout into public/api/openapi.json.

GoWave endpoints outside the contract come from scripts/openapi-gowave.json.
GoWave changes to contract endpoints are patched in below.

Usage: python3 scripts/sync_openapi.py [path/to/gowave]
"""
import json
import os
import sys

here = os.path.dirname(__file__)
repo = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/GoWave")
source = os.path.join(repo, "backend-go/internal/contracts/openapi.json")
overlay_path = os.path.join(here, "openapi-gowave.json")
target = os.path.join(here, "..", "public/api/openapi.json")

spec = json.load(open(source, encoding="utf-8"))
overlay = json.load(open(overlay_path, encoding="utf-8"))
contract = spec.get("info", {}).get("version", "")
spec["info"]["title"] = "GoWave API"
spec["info"]["description"] = (
    f"GoWave implements the Remnawave backend API, contract `@remnawave/backend-contract` {contract}. "
    "Requests go to your panel: `https://<panel domain>/api/...` with `Authorization: Bearer <token>`.\n\n"
    "Endpoints GoWave adds on top of the contract are under **GoWave extensions**."
)

# Extensions must not shadow the contract: if upstream adds the same route,
# drop it from the overlay instead of silently replacing it.
for path, ops in overlay["paths"].items():
    for method, op in ops.items():
        if method in spec["paths"].get(path, {}):
            sys.exit(f"{method.upper()} {path} is in the contract now, remove it from {overlay_path}")
        spec["paths"].setdefault(path, {})[method] = op
spec.setdefault("components", {}).setdefault("schemas", {}).update(overlay.get("schemas", {}))
spec["tags"] = overlay.get("tags", []) + [t for t in spec.get("tags", []) if t["name"] not in {o["name"] for o in overlay.get("tags", [])}]


def json_body(op):
    return op["requestBody"]["content"]["application/json"]["schema"]


def response_body(op):
    return op["responses"]["default"]["content"]["application/json"]["schema"]["properties"]["response"]


# UpdateNodeCommand: GoWave accepts how the traffic counter starts.
json_body(spec["paths"]["/api/nodes"]["patch"])["properties"]["trafficTrackingStart"] = {
    "type": "string",
    "enum": ["keep", "zero", "period"],
    "description": (
        "GoWave extension. Applies when this update turns `isTrafficTrackingActive` on: "
        "`keep` keeps the bytes counted since the last reset (the default, as upstream), "
        "`zero` starts from nothing, `period` counts the current period from the usage history."
    ),
}

# Yandex sign-in is removed; the fields stay for contract compatibility.
YANDEX = "Not supported by GoWave: Yandex sign-in is removed. The provider is always disabled and saved settings are discarded."
for path in ("/api/auth/oauth2/authorize", "/api/auth/oauth2/callback"):
    json_body(spec["paths"][path]["post"])["properties"]["provider"]["description"] = "`yandex` is not supported by GoWave."
settings = spec["paths"]["/api/remnawave-settings"]
for schema in (
    json_body(settings["patch"])["properties"]["oauth2Settings"],
    response_body(settings["get"])["properties"]["oauth2Settings"]["anyOf"][0],
    response_body(settings["patch"])["properties"]["oauth2Settings"]["anyOf"][0],
):
    schema["properties"]["yandex"]["description"] = YANDEX

json.dump(spec, open(target, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(
    f"wrote {os.path.normpath(target)} (contract {contract}, {len(spec.get('paths', {}))} paths, "
    f"{sum(len(ops) for ops in overlay['paths'].values())} GoWave extensions)"
)
