#!/usr/bin/env python3
"""Turn benchmark results into data for the docs site:
src/data/benchmarks.json (landing bars) and src/data/benchmark-tables.json
(full tables on the benchmarks page), and copy the SVG charts."""
import json
import os
import shutil
import statistics
from collections import defaultdict

LAB = os.path.expanduser("~/gowave-lab/results")
SITE = os.path.expanduser("~/gowave-docs")
LEVEL = 32  # landing bars compare at this many concurrent clients


def load(directory):
    rows = defaultdict(list)
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        if name.endswith("-warmup") or not os.path.isfile(os.path.join(path, "result.json")):
            continue
        result = json.load(open(os.path.join(path, "result.json")))
        latency = json.load(open(os.path.join(path, "summary.json")))["metrics"]["bench_service_latency"]["values"]
        rows[(result["workload"], result["mode"], result["level"], result["target"])].append({
            "rps": result["successful_rps"], "p50": latency["med"], "p99": latency["p(99)"],
            "memory": result["memory"]["time_weighted_average_bytes"] / 2**20, "passed": result["passed"],
        })
    return {key: {field: statistics.median(run[field] for run in runs) for field in ("rps", "p50", "p99", "memory")}
            | {"passed": all(run["passed"] for run in runs)} for key, runs in rows.items()}


concurrency = load(os.path.join(LAB, "full-concurrency"))
rate = load(os.path.join(LAB, "full-rate"))
startup = json.load(open(os.path.join(LAB, "full-startup", "charts.json")))["startup"]
startup_ms = {target: statistics.median(t["api_ready_ms"] for t in startup if t["target"] == target)
              for target in ("gowave", "remnawave")}
memory = {target: statistics.median(v["memory"] for k, v in concurrency.items() if k[3] == target)
          for target in ("gowave", "remnawave")}


def bars(workload):
    return [{"label": label, "value": round(concurrency[(workload, "concurrency", LEVEL, target)]["rps"])}
            for label, target in (("GoWave", "gowave"), ("Remnawave", "remnawave"))]


landing = {
    "note": {
        "ru": f"Docker, по 2 CPU и 2 ГиБ на панель, PostgreSQL 17 (1 CPU) у каждой, 1000 пользователей, {LEVEL} одновременных клиента. Медиана двух прогонов по 20 с. Remnawave 3.4.5.",
        "en": f"Docker, 2 CPU and 2 GiB per panel, PostgreSQL 17 (1 CPU) each, 1,000 users, {LEVEL} concurrent clients. Median of two 20 s runs. Remnawave 3.4.5.",
    },
    "groups": [
        {"title": {"ru": "Чтение API", "en": "API reads"},
         "subtitle": {"ru": "список, карточка, статистика, ноды", "en": "list, detail, stats, nodes"},
         "unit": {"ru": "запросов/с", "en": "requests/s"}, "higherIsBetter": True, "rows": bars("reads")},
        {"title": {"ru": "Подписки", "en": "Subscriptions"},
         "subtitle": {"ru": "Xray JSON, Mihomo, sing-box", "en": "Xray JSON, Mihomo, sing-box"},
         "unit": {"ru": "запросов/с", "en": "requests/s"}, "higherIsBetter": True, "rows": bars("subscriptions")},
        {"title": {"ru": "Память под нагрузкой", "en": "Memory under load"},
         "subtitle": {"ru": "контейнер панели, медиана", "en": "panel container, median"},
         "unit": {"ru": "МиБ", "en": "MiB"}, "higherIsBetter": False,
         "rows": [{"label": "GoWave", "value": round(memory["gowave"])}, {"label": "Remnawave", "value": round(memory["remnawave"])}]},
        {"title": {"ru": "Запуск", "en": "Startup"},
         "subtitle": {"ru": "до первого ответа API", "en": "until the API answers"},
         "unit": {"ru": "мс", "en": "ms"}, "higherIsBetter": False,
         "rows": [{"label": "GoWave", "value": round(startup_ms["gowave"])}, {"label": "Remnawave", "value": round(startup_ms["remnawave"])}]},
    ],
}

tables = {
    "concurrency": [
        {"workload": w, "level": l,
         "gowave": {k: round(v, 2) for k, v in concurrency[(w, "concurrency", l, "gowave")].items() if k != "passed"} | {"passed": concurrency[(w, "concurrency", l, "gowave")]["passed"]},
         "remnawave": {k: round(v, 2) for k, v in concurrency[(w, "concurrency", l, "remnawave")].items() if k != "passed"} | {"passed": concurrency[(w, "concurrency", l, "remnawave")]["passed"]}}
        for w, _, l, t in sorted(concurrency) if t == "gowave"
    ],
    "rate": [
        {"workload": w, "level": l,
         "gowave": {k: round(rate[(w, "rate", l, "gowave")][k], 2) for k in ("p50", "p99")},
         "remnawave": {k: round(rate[(w, "rate", l, "remnawave")][k], 2) for k in ("p50", "p99")}}
        for w, _, l, t in sorted(rate) if t == "gowave"
    ],
    "startup": {t: round(v) for t, v in startup_ms.items()},
    "memory": {t: round(v) for t, v in memory.items()},
}

os.makedirs(os.path.join(SITE, "src/data"), exist_ok=True)
json.dump(landing, open(os.path.join(SITE, "src/data/benchmarks.json"), "w"), indent=2, ensure_ascii=False)
json.dump(tables, open(os.path.join(SITE, "src/data/benchmark-tables.json"), "w"), indent=2, ensure_ascii=False)
charts = os.path.join(SITE, "public/benchmarks")
os.makedirs(charts, exist_ok=True)
for name in os.listdir(os.path.join(LAB, "full-figures")):
    if name.endswith(".svg"):
        shutil.copy(os.path.join(LAB, "full-figures", name), charts)
print(json.dumps({"startup_ms": startup_ms, "memory_mib": memory, "landing": [g["rows"] for g in landing["groups"]]}, indent=1))
