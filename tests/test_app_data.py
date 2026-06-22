import json
from pathlib import Path

import pandas as pd
import pytest

from parkvision import app_data


def test_artifact_files_covers_all_eight():
    expected = {
        "scored_zones", "hotspots", "forecast", "forecast_metrics",
        "deploy_plan", "roi_curve", "blind_spots", "validation",
        "cis_sensitivity",
    }
    assert set(app_data.ARTIFACT_FILES) == expected


def test_read_parquet_reads_real_file(tmp_path):
    df = pd.DataFrame({"zone_id": ["a", "b"], "cis": [88.5, 12.0]})
    p = tmp_path / "scored_zones.parquet"
    df.to_parquet(p)
    out = app_data._read_parquet(p)
    assert list(out.columns) == ["zone_id", "cis"]
    assert out.loc[0, "cis"] == 88.5
    assert len(out) == 2


def test_read_json_reads_real_file(tmp_path):
    p = tmp_path / "validation.json"
    p.write_text(json.dumps({"top_n": 20, "overlap_pct": 85.0}))
    out = app_data._read_json(p)
    assert out["overlap_pct"] == 85.0
    assert out["top_n"] == 20


def test_read_parquet_missing_file_raises_clear_error(tmp_path):
    missing = tmp_path / "does_not_exist.parquet"
    with pytest.raises(FileNotFoundError) as exc:
        app_data._read_parquet(missing)
    msg = str(exc.value)
    assert "Artifact not found" in msg
    assert str(missing) in msg
    assert "build_artifacts" in msg


def test_read_json_missing_file_raises_clear_error(tmp_path):
    missing = tmp_path / "missing.json"
    with pytest.raises(FileNotFoundError) as exc:
        app_data._read_json(missing)
    assert "Artifact not found" in str(exc.value)
    assert "build_artifacts" in str(exc.value)


def test_load_all_reads_all_eight(tmp_path, monkeypatch):
    # Build minimal fakes for all 8 artifacts in a temp ARTIFACTS dir.
    monkeypatch.setattr(app_data, "ARTIFACTS", tmp_path)
    pd.DataFrame({"zone_id": ["a"], "cis": [88.5], "station": ["S"],
                  "high_impact": [3], "lat": [12.9], "lon": [77.6]}
                 ).to_parquet(tmp_path / "scored_zones.parquet")
    pd.DataFrame({"hotspot_id": [0], "total_cis": [100.0], "mean_cis": [50.0],
                  "n_zones": [2], "lat": [12.9], "lon": [77.6]}
                 ).to_parquet(tmp_path / "hotspots.parquet")
    pd.DataFrame({"zone_id": ["a"], "risk": [5.0], "slope": [0.1],
                  "rising": [True]}).to_parquet(tmp_path / "forecast.parquet")
    pd.DataFrame({"rank": [1], "zone_id": ["a"], "lat": [12.9], "lon": [77.6],
                  "cis": [88.5], "high_impact_covered": [3], "cis_covered": [88.5],
                  "n_zones_covered": [1]}).to_parquet(tmp_path / "deploy_plan.parquet")
    pd.DataFrame({"k": [5], "covered_pct": [10.0], "baseline_pct": [1.5],
                  "efficiency": [6.7], "marginal_gain": [10.0]}
                 ).to_parquet(tmp_path / "roi_curve.parquet")
    pd.DataFrame({"zone_id": ["a"], "lat": [12.9], "lon": [77.6], "cis": [88.5],
                  "high_impact": [3], "n_violations": [10], "station": ["S"],
                  "busy_station": [False], "blindspot_rank": [1]}
                 ).to_parquet(tmp_path / "blind_spots.parquet")
    (tmp_path / "forecast_metrics.json").write_text(
        json.dumps({"spearman": 0.8488, "mae": 2.88}))
    (tmp_path / "validation.json").write_text(
        json.dumps({"top_n": 20, "overlap_pct": 85.0, "n_top_zones": 20}))
    (tmp_path / "cis_sensitivity.json").write_text(
        json.dumps({"weight_perturbation_mean_spearman_rho": 0.91,
                    "leave_one_out_jaccard": {"recency": 0.7}}))

    app_data.load_all.clear()  # drop any cached value from a prior test
    data = app_data.load_all()
    assert set(data) == set(app_data.ARTIFACT_FILES)
    assert isinstance(data["scored_zones"], pd.DataFrame)
    assert data["forecast_metrics"]["spearman"] == 0.8488
    assert data["validation"]["overlap_pct"] == 85.0
