import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

_EARTH_M = 6_371_000.0

def detect_hotspots(scored_zones, eps_m=300, min_samples=2):
    out = scored_zones.copy()
    if out.empty:
        out["hotspot_id"] = pd.Series(dtype=int)
        return out
    coords = np.radians(out[["lat", "lon"]].to_numpy())
    labels = DBSCAN(eps=eps_m / _EARTH_M, min_samples=min_samples,
                    metric="haversine").fit_predict(coords)
    out["hotspot_id"] = labels.astype(int)
    return out

def rank_hotspots(zones_with_hotspots, top_n=10):
    df = zones_with_hotspots[zones_with_hotspots["hotspot_id"] >= 0]
    agg = (df.groupby("hotspot_id")
             .agg(total_cis=("cis", "sum"), mean_cis=("cis", "mean"),
                  n_zones=("zone_id", "size"), lat=("lat", "mean"), lon=("lon", "mean"))
             .reset_index()
             .sort_values("total_cis", ascending=False)
             .head(top_n)
             .reset_index(drop=True))
    return agg[["hotspot_id", "total_cis", "mean_cis", "n_zones", "lat", "lon"]]
