import pytest
import pandas as pd
from parkvision import ingest, config

@pytest.fixture(scope="module")
def real():
    if not config.DATA_PATH.exists():
        pytest.skip("real CSV not present")
    return ingest.load_violations()

HIGH = {k for k, v in config.SEVERITY_WEIGHTS.items() if v == 1.0}

def test_record_count_and_no_nan_coords(real):
    # 298450 raw - 5 rows with corrupt/unparseable created_datetime dropped
    assert real["id"].nunique() == 298445
    assert real["latitude"].notna().all()
    assert real["longitude"].notna().all()
    assert real["dt_ist"].notna().all()

def test_high_impact_share_is_about_9pct(real):
    by_id = real.groupby("id")["violation"].apply(lambda s: bool(set(s) & HIGH))
    share = by_id.mean() * 100
    assert 8.5 <= share <= 9.9, f"high-impact share {share:.1f}% off expected 9.2%"

def test_junction_share_is_about_50pct(real):
    by_id = real.groupby("id")["junction_name"].first().fillna("No Junction")
    share = (by_id != "No Junction").mean() * 100
    assert 49.0 <= share <= 52.0, f"junction share {share:.1f}% off expected 50.5%"

def test_enforcement_timing_columns_are_empty():
    """Guard test: closed_datetime and action_taken_timestamp are 100% null in the raw CSV.

    This verifies that there is no enforcement-resolution-timing signal in the dataset.
    If these columns ever become populated, this test will fail and alert developers.
    """
    if not config.DATA_PATH.exists():
        pytest.skip("real CSV not present")

    raw_df = pd.read_csv(config.DATA_PATH, low_memory=False)

    # Both columns should exist but be entirely null
    assert "closed_datetime" in raw_df.columns, "closed_datetime column missing from raw CSV"
    assert "action_taken_timestamp" in raw_df.columns, "action_taken_timestamp column missing from raw CSV"

    # Assert they are 100% empty
    assert raw_df["closed_datetime"].isna().all(), "closed_datetime has non-null values"
    assert raw_df["action_taken_timestamp"].isna().all(), "action_taken_timestamp has non-null values"
