import pandas as pd
from parkvision import cis

def _v(id, lat, lon, violation, vtype="CAR", junction="No Junction", road_type="road", hour=9, date="2024-01-01"):
    return {"id": id, "latitude": lat, "longitude": lon, "violation": violation,
            "vehicle_type": vtype, "junction_name": junction, "road_type": road_type,
            "police_station": "S", "validation_status": "approved",
            "dt_ist": pd.Timestamp(date), "hour": hour, "dow": 0, "date": pd.Timestamp(date).date()}

def test_assign_zone_groups_nearby_points():
    df = pd.DataFrame([_v("a", 12.9700, 77.5900, "NO PARKING"),
                       _v("b", 12.97001, 77.59001, "NO PARKING")])
    out = cis.assign_zone(df)
    assert out["zone_id"].nunique() == 1

def test_score_in_range_and_ranks_high_impact_higher():
    rows = []
    for d in range(1, 11):
        rows.append(_v(f"h{d}", 12.9700, 77.5900, "PARKING IN A MAIN ROAD",
                       vtype="BUS (BMTC/KSRTC)", junction="BTP082 - KR Market Junction",
                       road_type="arterial", hour=9, date=f"2024-01-{d:02d}"))
    rows.append(_v("l1", 12.8000, 77.7000, "DEFECTIVE NUMBER PLATE",
                  vtype="SCOOTER", road_type="residential", hour=14, date="2024-01-01"))
    z = cis.score_zones(pd.DataFrame(rows))
    assert z["cis"].between(0, 100).all()
    assert z["cis"].notna().all()
    assert {"c_severity","c_density","c_junction","c_roadtype","c_vehicle","c_recurrence"} <= set(z.columns)
    assert z.iloc[0]["zone_id"] == cis.assign_zone(pd.DataFrame([rows[0]]))["zone_id"].iloc[0]

def test_score_zones_emits_high_impact_count():
    rows = []
    # zone H: 3 high-impact (sev==1.0) + 1 medium
    for d in range(1, 4):
        rows.append(_v(f"h{d}", 12.9700, 77.5900, "PARKING IN A MAIN ROAD",
                       junction="BTP082 - KR Market Junction", date=f"2024-01-{d:02d}"))
    rows.append(_v("h4", 12.9700, 77.5900, "WRONG PARKING", date="2024-01-04"))
    z = cis.score_zones(pd.DataFrame(rows))
    assert "high_impact" in z.columns
    assert int(z.iloc[0]["high_impact"]) == 3        # only the 3 sev==1.0 rows

def test_score_zones_emits_dominant_station():
    rows = [
        _v("a", 12.9700, 77.5900, "NO PARKING"),
        _v("b", 12.97001, 77.59001, "NO PARKING"),
        _v("c", 12.97002, 77.59002, "NO PARKING"),
    ]
    df = pd.DataFrame(rows)
    df.loc[df["id"].isin(["a", "b"]), "police_station"] = "City Market"
    df.loc[df["id"] == "c", "police_station"] = "Madiwala"
    z = cis.score_zones(df)
    assert "station" in z.columns
    assert z.iloc[0]["station"] == "City Market"     # 2 of 3 -> dominant
