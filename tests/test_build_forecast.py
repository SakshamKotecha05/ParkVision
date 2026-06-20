import json
import pandas as pd
from parkvision import build_artifacts

def test_build_writes_forecast_and_deploy_artifacts(raw_csv, tmp_path):
    summary = build_artifacts.build(out_dir=tmp_path, data_path=raw_csv)
    for f in ["forecast.parquet", "forecast_metrics.json", "deploy_plan.parquet",
              "roi_curve.parquet", "blind_spots.parquet"]:
        assert (tmp_path / f).exists(), f
    fc = pd.read_parquet(tmp_path / "forecast.parquet")
    assert list(fc.columns) == ["zone_id", "risk", "slope", "rising"]      # schema even if empty
    dp = pd.read_parquet(tmp_path / "deploy_plan.parquet")
    assert {"rank", "zone_id", "high_impact_covered"} <= set(dp.columns)
    m = json.loads((tmp_path / "forecast_metrics.json").read_text())
    assert "spearman" in m and "framing" in m
    assert {"spearman", "covered_pct", "efficiency", "recommended_k"} <= set(summary)
