"""locustfile.py — ParkVision API load-test harness.

Targets the LOCAL uvicorn api.main:app only (never a public URL). Weighted
tasks hit the read endpoints. At events.quitting, writes
artifacts/load_test_results.json (aggregate + per-endpoint blocks). Attribute
names match locust's StatsEntry (total_rps, get_response_time_percentile,
fail_ratio, num_requests, num_failures).
"""
from __future__ import annotations

import json
from pathlib import Path

from locust import HttpUser, between, events, task

_RESULTS_PATH = Path("artifacts/load_test_results.json")


class ParkVisionApiUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(4)
    def zones(self):
        self.client.get("/zones?top_n=20&min_cis=0", name="zones")

    @task(3)
    def hotspots(self):
        self.client.get("/hotspots?top_n=10", name="hotspots")

    @task(2)
    def forecast(self):
        self.client.get("/forecast?top_n=20", name="forecast")

    @task(1)
    def deploy_plan(self):
        self.client.get("/deploy-plan", name="deploy_plan")

    @task(1)
    def blind_spots(self):
        self.client.get("/blind-spots", name="blind_spots")


@events.quitting.add_listener
def _write_results(environment, **kwargs):
    stats = environment.stats
    by_endpoint = {}
    for (name, method), entry in stats.entries.items():
        by_endpoint[name] = {
            "method": method,
            "num_requests": entry.num_requests,
            "num_failures": entry.num_failures,
            "rps": entry.total_rps,
            "p50_ms": entry.get_response_time_percentile(0.50),
            "p95_ms": entry.get_response_time_percentile(0.95),
        }
    result = {
        "aggregate": {
            "num_requests": stats.total.num_requests,
            "num_failures": stats.total.num_failures,
            "rps": stats.total.total_rps,
            "p50_ms": stats.total.get_response_time_percentile(0.50),
            "p95_ms": stats.total.get_response_time_percentile(0.95),
            "fail_ratio": stats.total.fail_ratio,
        },
        "by_endpoint": by_endpoint,
    }
    _RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _RESULTS_PATH.write_text(json.dumps(result, indent=2))
