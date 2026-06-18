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
