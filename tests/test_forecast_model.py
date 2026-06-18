import numpy as np
import pandas as pd
from parkvision import forecast

def _panel(n_days=50):
    """Two zones: A consistently high risk, B consistently low. Includes static morning_share."""
    rows = []
    base = pd.Timestamp("2024-01-01")
    for i in range(n_days):
        d = base + pd.Timedelta(days=i)
        rows.append({"zone_id": "A", "period": d, "lat": 12.97, "lon": 77.59,
                     "dow": d.dayofweek, "n": 10, "risk": 10.0, "roll7": 10.0, "roll28": 10.0})
        rows.append({"zone_id": "B", "period": d, "lat": 12.80, "lon": 77.70,
                     "dow": d.dayofweek, "n": 1, "risk": 1.0, "roll7": 1.0, "roll28": 1.0})
    panel = pd.DataFrame(rows)
    static = pd.DataFrame({"zone_id": ["A", "B"], "morning_share": [0.9, 0.1], "total_n": [500, 50]})
    return panel.merge(static[["zone_id", "morning_share"]], on="zone_id", how="left"), static

def test_predict_risk_schema_and_nonnegative():
    panel, static = _panel()
    model = forecast.train_forecaster(panel)
    feats = forecast.latest_zone_features(panel, static)
    out = forecast.predict_risk(model, feats, when="2024-03-04")
    assert list(out.columns) == ["zone_id", "risk"]
    assert len(out) == 2
    assert (out["risk"] >= 0).all()

def test_latest_features_one_row_per_zone_with_morning_share():
    panel, static = _panel()
    feats = forecast.latest_zone_features(panel, static)
    assert set(feats.columns) >= {"zone_id", "lat", "lon", "roll7", "roll28", "morning_share"}
    assert feats["zone_id"].nunique() == len(feats) == 2

def test_high_history_zone_outranks_low():
    panel, static = _panel()
    model = forecast.train_forecaster(panel)
    feats = forecast.latest_zone_features(panel, static)
    out = forecast.predict_risk(model, feats, when="2024-03-04").set_index("zone_id")
    assert out.loc["A", "risk"] > out.loc["B", "risk"]
