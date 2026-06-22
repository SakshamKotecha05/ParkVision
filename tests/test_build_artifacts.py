import json
import pandas as pd
from pathlib import Path
from parkvision import build_artifacts
from parkvision.config import ARTIFACTS

def test_build_writes_artifacts(raw_csv, tmp_path):
    summary = build_artifacts.build(out_dir=tmp_path, data_path=raw_csv)
    assert (tmp_path / "scored_zones.parquet").exists()
    assert (tmp_path / "hotspots.parquet").exists()
    assert (tmp_path / "validation.json").exists()
    z = pd.read_parquet(tmp_path / "scored_zones.parquet")
    assert z["cis"].between(0, 100).all() and z["cis"].notna().all()
    v = json.loads((tmp_path / "validation.json").read_text())
    assert set(v) >= {"top_n", "overlap_pct", "n_top_zones"}
    assert summary["n_zones"] == len(z)
    assert {"n_officers", "top_officer_share", "single_source"}.issubset(set(z.columns))
    assert {"repeat_offender_share", "n_repeat_vehicles"}.issubset(set(z.columns))


def test_build_writes_cis_sensitivity(tmp_path):
    # Builds against the real CSV into a temp dir; asserts the new artifact.
    from parkvision import build_artifacts
    from parkvision.config import DATA_PATH
    if not Path(DATA_PATH).exists():
        import pytest
        pytest.skip("source CSV not present")
    summary = build_artifacts.build(out_dir=tmp_path, data_path=DATA_PATH)
    sens_path = tmp_path / "cis_sensitivity.json"
    assert sens_path.exists()
    rep = json.loads(sens_path.read_text())
    assert "weight_perturbation_mean_spearman_rho" in rep
    assert "cis_weight_robustness_rho" in summary
