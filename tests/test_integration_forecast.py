import math
import pytest
from parkvision import ingest, cis, forecast, deploy, config

@pytest.fixture(scope="module")
def real_violations():
    if not config.DATA_PATH.exists():
        pytest.skip("real CSV not present")
    return ingest.load_violations()

def test_backtest_spearman_is_strong(real_violations):
    r = forecast.backtest(real_violations)
    assert not math.isnan(r["spearman"])
    assert -1.0 <= r["spearman"] <= 1.0
    assert r["spearman"] > 0.3, f"zone-ranking Spearman {r['spearman']:.3f} below honesty floor"

def test_optimizer_beats_random_on_real_data(real_violations):
    z = cis.score_zones(real_violations)
    _, stats = deploy.plan_deployment(z, k=20, n_baseline=25, seed=0)
    assert stats["covered_pct"] > stats["baseline_pct"]
    assert stats["efficiency"] > 1.5, f"efficiency {stats['efficiency']} too low vs random patrol"
