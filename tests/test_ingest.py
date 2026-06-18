import math
import pandas as pd
from parkvision import ingest

def test_parse_violation_types():
    assert ingest.parse_violation_types('["WRONG PARKING","NO PARKING"]') == ["WRONG PARKING", "NO PARKING"]
    assert ingest.parse_violation_types("NULL") == []
    assert ingest.parse_violation_types(float("nan")) == []
    assert ingest.parse_violation_types("[broken") == []

def test_load_explodes_and_filters(raw_csv):
    df = ingest.load_violations(raw_csv)
    # A->2 rows, B->1 row, C dropped (out of bbox) => 3 rows
    assert len(df) == 3
    assert set(df["id"]) == {"A", "B"}
    assert (df.columns == ["id","latitude","longitude","violation","vehicle_type",
            "junction_name","road_type","police_station","validation_status",
            "dt_ist","hour","dow","date"]).all()
    assert df[df["id"] == "A"].iloc[0]["road_type"] == "main"
    assert df[df["id"] == "B"].iloc[0]["road_type"] == "cross"

def test_times_converted_to_ist(raw_csv):
    df = ingest.load_violations(raw_csv)
    a = df[df["id"] == "A"].iloc[0]
    assert a["hour"] == 8          # 02:30 UTC -> 08:00 IST
    b = df[df["id"] == "B"].iloc[0]
    assert b["hour"] == 23         # 18:00 UTC -> 23:30 IST

def test_classify_road_type():
    assert ingest.classify_road_type("Outer Ring Road, BTM Layout, Bengaluru") == "arterial"
    assert ingest.classify_road_type("NH 75, Somewhere") == "arterial"
    assert ingest.classify_road_type("18th Main Road, Block 2, Koramangala") == "main"
    assert ingest.classify_road_type("6th Cross Road, Manasa Layout") == "cross"
    assert ingest.classify_road_type("Kalidasa Road, Gandhinagar") == "road"
    assert ingest.classify_road_type("Koramangala 2nd Block") == "residential"
    assert ingest.classify_road_type("") == "unknown"
    assert ingest.classify_road_type(float("nan")) == "unknown"
