import math
import pandas as pd
from parkvision import forecast

def _rows_for(zone_lat, zone_lon, start, end, per_day, hour=9):
    rows = []
    for d in pd.date_range(start, end, freq="D"):
        for k in range(per_day):
            rows.append({"id": f"{zone_lat}_{d.date()}_{k}", "latitude": zone_lat, "longitude": zone_lon,
                         "violation": "PARKING IN A MAIN ROAD", "vehicle_type": "CAR",
                         "junction_name": "No Junction", "road_type": "main", "police_station": "S",
                         "validation_status": "approved",
                         "dt_ist": pd.Timestamp(f"{d.date()} {hour:02d}:00:00", tz="Asia/Kolkata"),
                         "hour": hour, "dow": d.dayofweek, "date": d.date()})
    return rows

def test_backtest_returns_metrics_over_temporal_split():
    # Busy zone (5/day) and quiet zone (1/day), Jan 1 -> Mar 20, persistent pattern.
    rows = (_rows_for(12.9700, 77.5900, "2024-01-01", "2024-03-20", per_day=5) +
            _rows_for(12.8000, 77.7000, "2024-01-01", "2024-03-20", per_day=1))
    r = forecast.backtest(pd.DataFrame(rows), train_end="2024-02-29", valid_end="2024-03-31", min_total=5)
    assert set(r) == {"spearman", "mae", "n_train", "n_valid", "n_zones_valid", "train_end", "valid_end"}
    assert r["n_train"] > 0 and r["n_valid"] > 0
    assert -1.0 <= r["spearman"] <= 1.0 and not math.isnan(r["spearman"])
    assert r["mae"] >= 0.0

def test_backtest_empty_valid_window_is_nan():
    rows = _rows_for(12.9700, 77.5900, "2024-01-01", "2024-02-10", per_day=5)   # nothing in March
    r = forecast.backtest(pd.DataFrame(rows), train_end="2024-02-29", valid_end="2024-03-31", min_total=5)
    assert math.isnan(r["spearman"]) and r["n_valid"] == 0
