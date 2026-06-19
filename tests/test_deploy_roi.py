import pandas as pd
from parkvision import deploy
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
