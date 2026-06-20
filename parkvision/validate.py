import pandas as pd
import numpy as np

def junction_overlap(scored_zones, top_n=20, thresh=0.5):
    top = scored_zones.head(top_n)
    n = len(top)
    if n == 0:
        return {"top_n": top_n, "overlap_pct": 0.0, "n_top_zones": 0}
    overlap = (top["junction_prox"] >= thresh).mean() * 100
    return {"top_n": top_n, "overlap_pct": round(float(overlap), 1), "n_top_zones": int(n)}

def blind_spots(scored_zones, top_n_stations=10, top=20):
    cols = ["zone_id", "lat", "lon", "cis", "high_impact", "n_violations",
            "station", "busy_station", "blindspot_rank"]
    z = scored_zones.copy()
    by_station = z.groupby("station")["n_violations"].sum().sort_values(ascending=False)
    busy = set(by_station.head(top_n_stations).index)
    z["busy_station"] = z["station"].isin(busy)

    under = (z[~z["busy_station"]]
               .sort_values("cis", ascending=False)
               .head(top)
               .reset_index(drop=True))
    under["blindspot_rank"] = np.arange(1, len(under) + 1)
    return under[cols]
