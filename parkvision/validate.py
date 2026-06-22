import pandas as pd
import numpy as np
from .cis import assign_zone
from .config import GEOHASH_PRECISION

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

def source_diversity(violations, precision=None):
    """Per-zone officer-source diversity: independent proof hotspots aren't one officer's beat."""
    if precision is None:
        precision = GEOHASH_PRECISION
    df = assign_zone(violations, precision)

    def _summarize(g):
        vc = g["created_by_id"].value_counts()
        n_officers = int(g["created_by_id"].nunique())
        top_officer_share = float(vc.iloc[0] / len(g))
        return pd.Series({
            "n_officers": n_officers,
            "top_officer_share": top_officer_share,
        })

    out = (df.groupby("zone_id").apply(_summarize, include_groups=False)
             .reset_index())
    out["n_officers"] = out["n_officers"].astype(int)
    out["single_source"] = out["top_officer_share"] > 0.8
    return out[["zone_id", "n_officers", "top_officer_share", "single_source"]]

def repeat_offenders(violations, min_count=5):
    """Per-zone share of violations from vehicles seen >= min_count times citywide."""
    df = assign_zone(violations, GEOHASH_PRECISION)

    vc = df["vehicle_number"].value_counts()
    df["is_repeat"] = df["vehicle_number"].map(vc) >= min_count

    share = df.groupby("zone_id")["is_repeat"].mean().rename("repeat_offender_share")
    n_repeat = (df[df["is_repeat"]].groupby("zone_id")["vehicle_number"].nunique()
                  .rename("n_repeat_vehicles"))

    out = (share.to_frame()
                .join(n_repeat, how="left")
                .reset_index())
    out["n_repeat_vehicles"] = out["n_repeat_vehicles"].fillna(0).astype(int)
    return out[["zone_id", "repeat_offender_share", "n_repeat_vehicles"]]
