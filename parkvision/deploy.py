"""Greedy max-coverage patrol optimizer + patrol-ROI curve (spec §4.5, §4A.3)."""
import numpy as np
import pandas as pd

_EARTH_M = 6_371_000.0
_PLAN_COLS = ["rank", "zone_id", "lat", "lon", "cis",
              "high_impact_covered", "cis_covered", "n_zones_covered"]


def _haversine_m(lat0, lon0, lat, lon):
    p0, p = np.radians(lat0), np.radians(lat)
    dlat = np.radians(lat - lat0)
    dlon = np.radians(lon - lon0)
    a = np.sin(dlat / 2) ** 2 + np.cos(p0) * np.cos(p) * np.sin(dlon / 2) ** 2
    return 2 * _EARTH_M * np.arcsin(np.sqrt(a))


def _random_baseline_pct(lat, lon, hi, k, radius_m, n_baseline, seed):
    n, total = len(lat), float(hi.sum())
    if total <= 0 or n == 0:
        return 0.0
    rng = np.random.default_rng(seed)
    accs = []
    for _ in range(n_baseline):
        idx = rng.choice(n, size=min(k, n), replace=False)
        covered = np.zeros(n, dtype=bool)
        for c in idx:
            covered |= _haversine_m(lat[c], lon[c], lat, lon) <= radius_m
        accs.append(hi[covered].sum() / total * 100.0)
    return float(np.mean(accs))


def plan_deployment(scored_zones, k, shift=None, radius_m=500, n_baseline=40, seed=0):
    z = scored_zones.sort_values("cis", ascending=False).reset_index(drop=True)
    lat = z["lat"].to_numpy(float); lon = z["lon"].to_numpy(float)
    hi = z["high_impact"].to_numpy(float); cisv = z["cis"].to_numpy(float)
    n = len(z); total_hi = float(hi.sum())

    covered = np.zeros(n, dtype=bool)
    rows = []
    for rank in range(1, min(k, n) + 1):
        avail = np.where(~covered)[0]
        if avail.size == 0:
            break
        c = int(avail[0])                                   # highest-cis uncovered (z is cis-sorted)
        disk = (_haversine_m(lat[c], lon[c], lat, lon) <= radius_m) & ~covered
        rows.append({"rank": rank, "zone_id": z.at[c, "zone_id"], "lat": lat[c], "lon": lon[c],
                     "cis": cisv[c], "high_impact_covered": float(hi[disk].sum()),
                     "cis_covered": float(cisv[disk].sum()), "n_zones_covered": int(disk.sum())})
        covered |= disk

    plan = pd.DataFrame(rows, columns=_PLAN_COLS)
    covered_hi = float(hi[covered].sum())
    covered_pct = 100.0 * covered_hi / total_hi if total_hi else 0.0
    base = _random_baseline_pct(lat, lon, hi, k, radius_m, n_baseline, seed)
    stats = {"k": int(k), "shift": shift, "radius_m": radius_m,
             "covered_high_impact": covered_hi, "total_high_impact": total_hi,
             "covered_pct": round(covered_pct, 1), "baseline_pct": round(base, 1),
             "efficiency": round(covered_pct / base, 1) if base > 0 else float("inf")}
    return plan, stats


def roi_curve(scored_zones, k_values=None, radius_m=500, n_baseline=20, seed=0):
    if k_values is None:
        k_values = [5, 10, 15, 20, 25, 30, 40, 50]
    rows, prev = [], 0.0
    for k in k_values:
        _, stats = plan_deployment(scored_zones, k, radius_m=radius_m,
                                   n_baseline=n_baseline, seed=seed)
        rows.append({"k": int(k), "covered_pct": stats["covered_pct"],
                     "baseline_pct": stats["baseline_pct"], "efficiency": stats["efficiency"],
                     "marginal_gain": round(stats["covered_pct"] - prev, 1)})
        prev = stats["covered_pct"]
    return pd.DataFrame(rows, columns=["k", "covered_pct", "baseline_pct", "efficiency", "marginal_gain"])


def recommend_k(curve, min_marginal=2.0):
    curve = curve.sort_values("k")
    below = curve[curve["marginal_gain"] < min_marginal]
    if len(below):
        return int(below.iloc[0]["k"])
    return int(curve["k"].iloc[-1])
