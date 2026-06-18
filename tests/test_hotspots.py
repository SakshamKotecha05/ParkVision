import pandas as pd
from parkvision import hotspots

def _zone(zid, lat, lon, cis):
    return {"zone_id": zid, "lat": lat, "lon": lon, "cis": cis}

def test_two_clusters_and_noise():
    rows = [
        _zone("a", 12.9700, 77.5900, 90), _zone("b", 12.9702, 77.5902, 80),  # cluster 1
        _zone("c", 12.9800, 77.6500, 70), _zone("d", 12.9802, 77.6502, 60),  # cluster 2
        _zone("e", 13.2000, 77.7700, 50),                                    # isolated -> noise
    ]
    out = hotspots.detect_hotspots(pd.DataFrame(rows), eps_m=300, min_samples=2)
    clustered = out[out["hotspot_id"] >= 0]["hotspot_id"].nunique()
    assert clustered == 2
    assert (out[out["zone_id"] == "e"]["hotspot_id"] == -1).all()

def test_rank_orders_by_total_cis():
    rows = [_zone("a", 12.97, 77.59, 90), _zone("b", 12.9701, 77.5901, 80),
            _zone("c", 12.98, 77.65, 30), _zone("d", 12.9801, 77.6501, 25)]
    out = hotspots.detect_hotspots(pd.DataFrame(rows), eps_m=300, min_samples=2)
    ranked = hotspots.rank_hotspots(out, top_n=10)
    assert list(ranked.columns) == ["hotspot_id","total_cis","mean_cis","n_zones","lat","lon"]
    assert ranked.iloc[0]["total_cis"] == 170   # 90+80 cluster on top
