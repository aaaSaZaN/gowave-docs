#!/usr/bin/env python3
"""Turn a gowave-bench GitHub Actions artifact into data for the benchmarks page.

Usage: python3 scripts/benchmark-data.py ARTIFACT_DIR

ARTIFACT_DIR is the unpacked `benchmark-full-N` artifact (it contains
concurrency/, rate/, startup/, figures/, config.json and machine.txt).
Writes src/data/benchmarks.json (landing bars), src/data/benchmark-tables.json
(tables on the benchmarks page) and copies the SVG charts to public/benchmarks.
"""
import json
from pathlib import Path
import re
import shutil
import statistics
import sys
from collections import defaultdict

SITE = Path(__file__).resolve().parent.parent
LEVEL = 32  # landing bars compare at this many concurrent clients
TARGETS = ("gowave", "remnawave")


def load(directory):
    rows = defaultdict(list)
    for path in directory.iterdir():
        if path.name.endswith("-warmup") or not (path / "result.json").is_file():
            continue
        result = json.loads((path / "result.json").read_text())
        latency = json.loads((path / "summary.json").read_text())["metrics"]["bench_service_latency"]["values"]
        rows[(result["workload"], result["mode"], result["level"], result["target"])].append({
            "rps": result["successful_rps"], "p50": latency["med"], "p99": latency["p(99)"],
            "memory": result["memory"]["time_weighted_average_bytes"] / 2**20, "passed": result["passed"],
        })
    return {key: {field: statistics.median(run[field] for run in runs) for field in ("rps", "p50", "p99", "memory")}
            | {"passed": all(run["passed"] for run in runs)} for key, runs in rows.items()}


def main(artifact):
    concurrency = load(artifact / "concurrency")
    rate = load(artifact / "rate")
    startup = json.loads((artifact / "startup/charts.json").read_text())["startup"]
    startup_ms = {t: statistics.median(s["api_ready_ms"] for s in startup if s["target"] == t) for t in TARGETS}
    memory = {t: statistics.median(v["memory"] for k, v in concurrency.items() if k[3] == t) for t in TARGETS}

    load_config = json.loads((artifact / "config.json").read_text())["load"]
    runs, seconds = load_config["repetitions"], load_config["duration_seconds"]
    cpus = re.search(r"^CPU\(s\):\s+(\d+)", (artifact / "machine.txt").read_text(), re.M).group(1)

    def bars(workload):
        return [{"label": label, "value": round(concurrency[(workload, "concurrency", LEVEL, target)]["rps"])}
                for label, target in (("GoWave", "gowave"), ("Remnawave", "remnawave"))]

    landing = {
        "note": {
            "ru": f"GitHub Actions ({cpus} vCPU), Docker, по 2 CPU и 2 ГиБ на панель, PostgreSQL 17 (1 CPU) у каждой, "
                  f"1000 пользователей, {LEVEL} одновременных клиента. Медиана {runs} прогонов по {seconds} с. Remnawave 3.4.5.",
            "en": f"GitHub Actions ({cpus} vCPU), Docker, 2 CPU and 2 GiB per panel, PostgreSQL 17 (1 CPU) each, "
                  f"1,000 users, {LEVEL} concurrent clients. Median of {runs} {seconds} s runs. Remnawave 3.4.5.",
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

    def row(results, workload, mode, level, target, fields=None):
        values = results[(workload, mode, level, target)]
        if fields:
            return {k: round(values[k], 2) for k in fields}
        return {k: round(v, 2) for k, v in values.items() if k != "passed"} | {"passed": values["passed"]}

    tables = {
        "concurrency": [{"workload": w, "level": l, **{t: row(concurrency, w, m, l, t) for t in TARGETS}}
                        for w, m, l, t in sorted(concurrency) if t == "gowave"],
        "rate": [{"workload": w, "level": l, **{t: row(rate, w, m, l, t, ("p50", "p99")) for t in TARGETS}}
                 for w, m, l, t in sorted(rate) if t == "gowave"],
        "startup": {t: round(v) for t, v in startup_ms.items()},
        "memory": {t: round(v) for t, v in memory.items()},
    }

    (SITE / "src/data").mkdir(parents=True, exist_ok=True)
    (SITE / "src/data/benchmarks.json").write_text(json.dumps(landing, indent=2, ensure_ascii=False) + "\n")
    (SITE / "src/data/benchmark-tables.json").write_text(json.dumps(tables, indent=2, ensure_ascii=False) + "\n")
    charts = SITE / "public/benchmarks"
    charts.mkdir(parents=True, exist_ok=True)
    for svg in (artifact / "figures").glob("*.svg"):
        shutil.copy(svg, charts)
    print(json.dumps({"startup_ms": startup_ms, "memory_mib": memory,
                      "landing": [g["rows"] for g in landing["groups"]]}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) != 2 or not (Path(sys.argv[1]) / "concurrency").is_dir():
        sys.exit(__doc__)
    main(Path(sys.argv[1]).resolve())
