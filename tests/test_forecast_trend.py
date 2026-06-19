import pandas as pd
import pygeohash as pgh
from parkvision import forecast
from parkvision.config import GEOHASH_PRECISION

Z = lambda la, lo: pgh.encode(la, lo, precision=GEOHASH_PRECISION)

def _week_rows(zid, lat, lon, weekly_counts):
    """weekly_counts[i] violations in ISO week i (Mondays from 2024-01-01)."""
    rows, base = [], pd.Timestamp("2024-01-01")   # a Monday
    for i, c in enumerate(weekly_counts):
        day = base + pd.Timedelta(weeks=i)
        for k in range(c):
            rows.append({"id": f"{zid}_{i}_{k}", "latitude": lat, "longitude": lon,
                         "violation": "PARKING IN A MAIN ROAD", "vehicle_type": "CAR",
                         "junction_name": "No Junction", "road_type": "main", "police_station": "S",
                         "validation_status": "approved",
                         "dt_ist": pd.Timestamp(f"{day.date()} 09:00:00", tz="Asia/Kolkata"),
                         "hour": 9, "dow": day.dayofweek, "date": day.date()})
    return rows

def test_rising_zone_flagged_and_flat_zone_not():
    rows = (_week_rows("up", 12.97, 77.59, [1, 2, 4, 7, 11]) +     # clearly increasing
            _week_rows("flat", 12.80, 77.70, [5, 5, 5, 5, 5]))     # flat
    t = forecast.zone_trend(pd.DataFrame(rows)).set_index("zone_id")
    assert list(forecast.zone_trend(pd.DataFrame(rows)).columns) == ["zone_id", "slope", "rising"]
    assert t.loc[Z(12.97, 77.59), "slope"] > 0 and bool(t.loc[Z(12.97, 77.59), "rising"]) is True
    assert abs(t.loc[Z(12.80, 77.70), "slope"]) < 1e-9 and bool(t.loc[Z(12.80, 77.70), "rising"]) is False

def test_short_history_zone_not_rising():
    rows = _week_rows("brief", 12.97, 77.59, [3, 9])               # only 2 weeks < min_weeks=3
    t = forecast.zone_trend(pd.DataFrame(rows), min_weeks=3).set_index("zone_id")
    assert t.loc[Z(12.97, 77.59), "slope"] == 0.0 and bool(t.loc[Z(12.97, 77.59), "rising"]) is False
