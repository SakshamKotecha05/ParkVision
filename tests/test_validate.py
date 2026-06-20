import pandas as pd
from parkvision import validate

def test_overlap_pct():
    # top-4 zones: 3 at junctions (prox>=0.5), 1 not -> 75%
    z = pd.DataFrame({
        "zone_id": list("abcd"),
        "cis": [90, 80, 70, 60],
        "junction_prox": [1.0, 0.8, 0.5, 0.0],
    })
    r = validate.junction_overlap(z, top_n=4)
    assert r == {"top_n": 4, "overlap_pct": 75.0, "n_top_zones": 4}

def test_handles_fewer_zones_than_top_n():
    z = pd.DataFrame({"zone_id": ["a"], "cis": [90], "junction_prox": [1.0]})
    r = validate.junction_overlap(z, top_n=20)
    assert r["n_top_zones"] == 1 and r["overlap_pct"] == 100.0

def test_blind_spots_flags_high_cis_under_quiet_station():
    z = pd.DataFrame({
        "zone_id": ["q1", "q2", "busy1", "busy2", "busy3"],
        "lat": [12.97, 12.98, 12.99, 13.00, 13.01],
        "lon": [77.59, 77.60, 77.61, 77.62, 77.63],
        "cis": [88.0, 40.0, 90.0, 85.0, 80.0],
        "high_impact": [30, 5, 50, 40, 35],
        "n_violations": [60, 20, 900, 800, 700],     # "Central" dominates the volume
        "station": ["Outpost", "Outpost", "Central", "Central", "Central"],
    })
    bs = validate.blind_spots(z, top_n_stations=1, top=10)
    assert list(bs.columns) == ["zone_id", "lat", "lon", "cis", "high_impact",
                                "n_violations", "station", "busy_station", "blindspot_rank"]
    # Central is the single busy station -> its zones are excluded; q1 (high cis, quiet station) leads.
    assert set(bs["zone_id"]) == {"q1", "q2"}
    assert bs.iloc[0]["zone_id"] == "q1" and bs.iloc[0]["blindspot_rank"] == 1
    assert (~bs["busy_station"]).all()

def test_blind_spots_top_truncates():
    z = pd.DataFrame({
        "zone_id": list("abcd") + ["busy"],
        "lat": [12.97, 12.98, 12.99, 13.0, 13.1], "lon": [77.59] * 5,
        "cis": [90.0, 80.0, 70.0, 60.0, 95.0], "high_impact": [9, 8, 7, 6, 50],
        "n_violations": [10, 10, 10, 10, 1000],          # "Central" dominates volume
        "station": ["Quiet"] * 4 + ["Central"],
    })
    bs = validate.blind_spots(z, top_n_stations=1, top=2)
    # Central is the single busy station -> the high-cis "busy" zone is excluded;
    # the 4 Quiet zones are under-served, and top=2 truncates to the 2 highest-cis.
    assert len(bs) == 2 and list(bs["zone_id"]) == ["a", "b"]
    assert "busy" not in set(bs["zone_id"])
