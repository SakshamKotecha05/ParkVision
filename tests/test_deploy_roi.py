import pandas as pd
from parkvision import deploy, config
from tests.test_deploy import _spread_zones   # reuse the spread fixture

def test_roi_curve_is_monotonic_and_has_columns():
    curve = deploy.roi_curve(_spread_zones(), k_values=[1, 2, 3], radius_m=300, n_baseline=10, seed=0)
    assert list(curve.columns) == ["k", "covered_pct", "baseline_pct", "efficiency", "marginal_gain"]
    assert list(curve["k"]) == [1, 2, 3]
    assert curve["covered_pct"].is_monotonic_increasing      # more patrols never cover less

def test_recommend_k_picks_the_elbow():
    curve = pd.DataFrame({
        "k": [5, 10, 15, 20],
        "covered_pct": [30.0, 45.0, 46.0, 46.5],             # big jump then flattens
        "baseline_pct": [1, 2, 3, 4], "efficiency": [1, 1, 1, 1],
        "marginal_gain": [30.0, 15.0, 1.0, 0.5],
    })
    assert deploy.recommend_k(curve, min_marginal=2.0) == 15  # first K with gain < 2.0

def test_recommend_k_falls_back_to_max_when_always_climbing():
    curve = pd.DataFrame({"k": [5, 10], "covered_pct": [10.0, 30.0], "baseline_pct": [1, 2],
                          "efficiency": [1, 1], "marginal_gain": [10.0, 20.0]})
    assert deploy.recommend_k(curve, min_marginal=2.0) == 10

def _toy_zones():
    # 6 zones; high_impact concentrated so coverage is well-defined.
    return pd.DataFrame({
        "zone_id": [f"z{i}" for i in range(6)],
        "lat": [12.97, 12.971, 12.98, 13.00, 13.05, 13.10],
        "lon": [77.59, 77.591, 77.60, 77.62, 77.65, 77.70],
        "cis": [90.0, 80.0, 70.0, 60.0, 50.0, 40.0],
        "high_impact": [50, 40, 30, 20, 10, 5],
    })


def test_config_exposes_single_baseline():
    assert config.DEPLOY_N_BASELINE == 40
    assert config.DEPLOY_SEED == 0
    assert config.DEPLOY_RADIUS_M == 500


def test_efficiency_is_single_valued_across_call_paths():
    z = _toy_zones()
    _, stats = deploy.plan_deployment(z, k=3)
    curve = deploy.roi_curve(z, k_values=[3])
    # Same K, same default baseline config -> identical efficiency.
    assert stats["efficiency"] == float(curve.loc[curve["k"] == 3, "efficiency"].iloc[0])
