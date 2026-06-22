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

def test_source_diversity_even_split_across_officers():
    # 4 violations in one zone (same lat/lon -> same geohash), 4 distinct officers
    v = pd.DataFrame({
        "latitude": [12.97, 12.97, 12.97, 12.97],
        "longitude": [77.59, 77.59, 77.59, 77.59],
        "created_by_id": ["o1", "o2", "o3", "o4"],
    })
    out = validate.source_diversity(v)
    assert len(out) == 1
    row = out.iloc[0]
    assert row["n_officers"] == 4
    assert row["top_officer_share"] == 0.25
    assert row["single_source"] == False  # noqa: E712

def test_source_diversity_single_officer_dominant_and_multi_zone():
    # zone "hot": 9/10 violations from one officer -> single_source True
    # zone "even": 4 violations split evenly across 4 officers -> single_source False
    v = pd.DataFrame({
        "latitude": [12.97] * 10 + [12.93] * 4,
        "longitude": [77.59] * 10 + [77.62] * 4,
        "created_by_id": ["dominant"] * 9 + ["other"] + ["o1", "o2", "o3", "o4"],
    })
    out = validate.source_diversity(v).set_index("zone_id")
    from parkvision.cis import assign_zone
    zoned = assign_zone(v)
    hot_id = zoned.loc[zoned["created_by_id"] == "dominant", "zone_id"].iloc[0]
    even_id = zoned.loc[zoned["created_by_id"] == "o1", "zone_id"].iloc[0]

    hot = out.loc[hot_id]
    assert hot["n_officers"] == 2
    assert hot["top_officer_share"] == 0.9
    assert hot["single_source"] == True  # noqa: E712

    even = out.loc[even_id]
    assert even["n_officers"] == 4
    assert even["top_officer_share"] == 0.25
    assert even["single_source"] == False  # noqa: E712

def test_repeat_offenders_zone_with_repeat_vehicle():
    # zone "hot" (lat/lon 12.97,77.59): 10 violations, 2 of which come from
    # vehicle "rep1" which appears 5 times citywide total (2 here, 3 elsewhere
    # in zone "other"). rep1 is a repeat vehicle (count==5 >= min_count=5).
    v = pd.DataFrame({
        "latitude": [12.97] * 10 + [12.93] * 3,
        "longitude": [77.59] * 10 + [77.62] * 3,
        "vehicle_number": (["rep1", "rep1"] + [f"v{i}" for i in range(8)]
                            + ["rep1", "rep1", "rep1"]),
    })
    out = validate.repeat_offenders(v).set_index("zone_id")
    from parkvision.cis import assign_zone
    zoned = assign_zone(v)
    hot_id = zoned[(zoned["latitude"] == 12.97)]["zone_id"].iloc[0]

    hot = out.loc[hot_id]
    assert hot["repeat_offender_share"] == 0.2  # 2/10
    assert hot["n_repeat_vehicles"] == 1

def test_repeat_offenders_zone_with_no_repeats():
    # zone with 5 violations, all distinct vehicles, none seen >=5 times citywide.
    v = pd.DataFrame({
        "latitude": [12.97] * 5,
        "longitude": [77.59] * 5,
        "vehicle_number": [f"v{i}" for i in range(5)],
    })
    out = validate.repeat_offenders(v).set_index("zone_id")
    row = out.iloc[0]
    assert row["repeat_offender_share"] == 0.0
    assert row["n_repeat_vehicles"] == 0
