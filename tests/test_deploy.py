import pandas as pd
from parkvision import deploy

def _z(zid, lat, lon, cis, hi):
    return {"zone_id": zid, "lat": lat, "lon": lon, "cis": cis, "high_impact": hi}

def _spread_zones():
    # 3 widely separated clusters (>1km apart) so radii never overlap; cluster heads carry the high-impact.
    return pd.DataFrame([
        _z("c1a", 12.9700, 77.5900, 95, 50), _z("c1b", 12.9702, 77.5902, 70, 10),  # cluster 1
        _z("c2a", 13.0200, 77.6500, 60, 40), _z("c2b", 13.0202, 77.6502, 40, 5),   # cluster 2
        _z("c3a", 12.9000, 77.7200, 30, 30),                                        # cluster 3 (lone)
    ])

def test_plan_columns_and_row_count():
    plan, stats = deploy.plan_deployment(_spread_zones(), k=2, radius_m=300, n_baseline=20, seed=0)
    assert list(plan.columns) == ["rank", "zone_id", "lat", "lon", "cis",
                                  "high_impact_covered", "cis_covered", "n_zones_covered"]
    assert len(plan) == 2
    assert list(plan["rank"]) == [1, 2]

def test_marginal_coverage_sums_to_total_covered():
    plan, stats = deploy.plan_deployment(_spread_zones(), k=2, radius_m=300, n_baseline=20, seed=0)
    assert abs(plan["high_impact_covered"].sum() - stats["covered_high_impact"]) < 1e-9
    # k=2 picks the two highest-cis cluster heads -> covers cluster1 (50+10) + cluster2 (40+5) = 105
    assert stats["covered_high_impact"] == 105

def test_optimizer_beats_random_baseline():
    plan, stats = deploy.plan_deployment(_spread_zones(), k=2, radius_m=300, n_baseline=50, seed=0)
    assert stats["covered_pct"] >= stats["baseline_pct"]
    assert stats["efficiency"] >= 1.0
