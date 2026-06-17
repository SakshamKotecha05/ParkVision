import pytest
from parkvision import ingest, config

@pytest.fixture(scope="module")
def real():
    if not config.DATA_PATH.exists():
        pytest.skip("real CSV not present")
    return ingest.load_violations()

HIGH = {k for k, v in config.SEVERITY_WEIGHTS.items() if v == 1.0}

def test_record_count_and_no_nan_coords(real):
    assert real["id"].nunique() == 298450      # 0 invalid coords dropped
    assert real["latitude"].notna().all()
    assert real["longitude"].notna().all()

def test_high_impact_share_is_about_9pct(real):
    by_id = real.groupby("id")["violation"].apply(lambda s: bool(set(s) & HIGH))
    share = by_id.mean() * 100
    assert 8.5 <= share <= 9.9, f"high-impact share {share:.1f}% off expected 9.2%"

def test_junction_share_is_about_50pct(real):
    by_id = real.groupby("id")["junction_name"].first().fillna("No Junction")
    share = (by_id != "No Junction").mean() * 100
    assert 49.0 <= share <= 52.0, f"junction share {share:.1f}% off expected 50.5%"
