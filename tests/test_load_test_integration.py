import json
from pathlib import Path

import pytest

_RESULTS = Path(__file__).resolve().parents[1] / "artifacts" / "load_test_results.json"


@pytest.mark.skipif(not _RESULTS.exists(),
                    reason="run scripts/run_load_test.sh first")
def test_results_shape():
    r = json.loads(_RESULTS.read_text())
    assert set(r.keys()) == {"aggregate", "by_endpoint"}
    agg = r["aggregate"]
    assert {"num_requests", "num_failures", "rps", "p50_ms", "p95_ms", "fail_ratio"} <= set(agg)
    assert agg["num_requests"] > 0
    assert agg["fail_ratio"] == 0.0
    assert set(r["by_endpoint"].keys()) <= {"zones", "hotspots", "forecast", "deploy_plan", "blind_spots"}
