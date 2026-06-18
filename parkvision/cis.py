import numpy as np
import pandas as pd
import pygeohash as pgh
from .config import (GEOHASH_PRECISION, CIS_WEIGHTS,
                     severity_weight, vehicle_footprint, road_weight)

def assign_zone(df, precision=GEOHASH_PRECISION):
    df = df.copy()
    df["zone_id"] = [pgh.encode(la, lo, precision=precision)
                     for la, lo in zip(df["latitude"], df["longitude"])]
    return df

def _minmax(s):
    lo, hi = float(s.min()), float(s.max())
    if hi <= lo:
        return pd.Series(0.0, index=s.index)
    return (s - lo) / (hi - lo)

def score_zones(violations, precision=GEOHASH_PRECISION, weights=CIS_WEIGHTS):
    df = assign_zone(violations, precision)
    df["sev"] = df["violation"].map(severity_weight)
    df["veh"] = df["vehicle_type"].map(vehicle_footprint)
    df["road"] = df["road_type"].map(road_weight)
    df["at_junction"] = df["junction_name"].fillna("No Junction").ne("No Junction")

    g = df.groupby("zone_id")
    z = pd.DataFrame({
        "lat": g["latitude"].mean(),
        "lon": g["longitude"].mean(),
        "n_violations": g.size(),
        "severity_sum": g["sev"].sum(),
        "junction_prox": g["at_junction"].mean(),
        "road_mean": g["road"].mean(),
        "vehicle_ftpt": g["veh"].mean(),
        "recurrence": g["date"].nunique(),
    })
    comp = pd.DataFrame({
        "c_severity": _minmax(z["severity_sum"]),
        "c_density": _minmax(np.log1p(z["n_violations"])),
        "c_junction": z["junction_prox"],
        "c_roadtype": z["road_mean"],
        "c_vehicle": z["vehicle_ftpt"],
        "c_recurrence": _minmax(np.log1p(z["recurrence"])),
    }, index=z.index)
    cis01 = (weights["severity"] * comp["c_severity"] +
             weights["density"]  * comp["c_density"] +
             weights["junction"] * comp["c_junction"] +
             weights["roadtype"] * comp["c_roadtype"] +
             weights["vehicle"]  * comp["c_vehicle"] +
             weights["recurrence"] * comp["c_recurrence"])
    z = z.join(comp)
    z["cis"] = (100 * cis01).round(1)
    return z.reset_index().sort_values("cis", ascending=False).reset_index(drop=True)
