import pandas as pd
from parkvision import artifact_store


def test_load_artifacts_returns_all_eight_keys():
    data = artifact_store.load_artifacts()
    expected = {
        "scored_zones", "hotspots", "forecast", "forecast_metrics",
        "deploy_plan", "roi_curve", "blind_spots", "validation",
    }
    assert set(data.keys()) == expected
    assert isinstance(data["scored_zones"], pd.DataFrame)
    assert isinstance(data["validation"], dict)
    assert "zone_id" in data["scored_zones"].columns


def test_known_zone_ids_is_nonempty_str_set():
    data = artifact_store.load_artifacts()
    ids = artifact_store.known_zone_ids(data["scored_zones"])
    assert isinstance(ids, set)
    assert len(ids) > 0
    assert all(isinstance(z, str) for z in list(ids)[:5])


def test_module_does_not_import_streamlit():
    import sys
    import importlib
    sys.modules.pop("streamlit", None)
    importlib.reload(artifact_store)
    assert "streamlit" not in sys.modules
