import json
import pandas as pd
from parkvision import build_artifacts

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
