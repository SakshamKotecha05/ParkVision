import pandas as pd
from parkvision import forecast

def _v(id, zid_lat, zid_lon, date, hour=9, violation="PARKING IN A MAIN ROAD"):
    return {"id": id, "latitude": zid_lat, "longitude": zid_lon, "violation": violation,
            "vehicle_type": "CAR", "junction_name": "No Junction", "road_type": "main",
            "police_station": "S", "validation_status": "approved",
            "dt_ist": pd.Timestamp(f"{date} {hour:02d}:00:00", tz="Asia/Kolkata"),
            "hour": hour, "dow": pd.Timestamp(date).dayofweek, "date": pd.Timestamp(date).date()}

def test_panel_filters_sparse_zones_and_has_columns():
    rows = []
    for d in range(1, 9):                                   # busy zone: 8 days -> kept
        rows.append(_v(f"b{d}", 12.9700, 77.5900, f"2024-01-{d:02d}"))
    rows.append(_v("s1", 12.8000, 77.7000, "2024-01-01"))   # sparse zone: 1 row -> dropped
    p = forecast.build_panel(pd.DataFrame(rows), min_total=5)
    assert list(p.columns) == ["zone_id", "period", "lat", "lon", "dow", "n", "risk", "roll7", "roll28"]
    assert p["zone_id"].nunique() == 1                      # only the busy zone survives

def test_lags_use_only_the_past_no_leakage():
    # 6 consecutive days, risk grows each day; roll7 on a day must equal the mean of PRIOR days only
    rows = []
    for i, d in enumerate(range(1, 7), start=1):
        for k in range(i):                                  # day d gets i violations (risk grows)
            rows.append(_v(f"r{d}_{k}", 12.9700, 77.5900, f"2024-01-{d:02d}"))
    p = forecast.build_panel(pd.DataFrame(rows), min_total=1).sort_values("period").reset_index(drop=True)
    # day 1 has no prior -> roll7 == 0 (NaN filled)
    assert p.iloc[0]["roll7"] == 0.0
    # day 3 risk = 3*sev(main=1.0)=3.0; roll7 = mean(prior risks 1.0, 2.0) = 1.5  (excludes day 3 itself)
    assert abs(p.iloc[2]["roll7"] - 1.5) < 1e-9

def test_static_features_morning_share_and_before_cutoff():
    rows = [_v("a", 12.97, 77.59, "2024-01-01", hour=9),    # peak (8-11)
            _v("b", 12.97, 77.59, "2024-01-02", hour=15),   # off-peak
            _v("c", 12.97, 77.59, "2024-03-10", hour=9)]    # peak, but AFTER cutoff
    s_all = forecast.zone_static_features(pd.DataFrame(rows))
    assert abs(s_all.iloc[0]["morning_share"] - (2/3)) < 1e-9
    s_train = forecast.zone_static_features(pd.DataFrame(rows), before="2024-02-29")
    assert abs(s_train.iloc[0]["morning_share"] - 0.5) < 1e-9   # only Jan rows count -> 1 of 2
