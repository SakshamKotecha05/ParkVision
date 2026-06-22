"""CIS weight-sensitivity report.

Re-weights the already-normalized CIS component columns (c_*) on a scored
zones frame to show how robust the top-N ranking is to the exact CIS weights.
Two methods (ported from the sibling ParkSight project, adapted to this
project's 6-component score):
  1. Dirichlet weight-perturbation -> mean Spearman rho of perturbed vs base
     top-N ranking (high => robust).
  2. Leave-one-factor-out -> Jaccard overlap of perturbed vs base top-N set
     (low for a factor => that factor dominates the ranking).
Pure: reads a DataFrame, returns a JSON-safe dict, writes nothing.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from parkvision.config import CIS_WEIGHTS

_FACTORS = list(CIS_WEIGHTS.keys())


def _cis_from_weights(z: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    return sum(weights[f] * z[f"c_{f}"] for f in _FACTORS)


def _top_order(z: pd.DataFrame, cis: pd.Series, top_n: int) -> list[str]:
    tmp = pd.DataFrame({"zone_id": z["zone_id"].astype(str), "cis": cis.to_numpy()})
    return list(tmp.sort_values(["cis", "zone_id"], ascending=[False, True]).head(top_n)["zone_id"])


def sensitivity_report(scored_zones, weights=None, n_perturbations=100, top_n=20, seed=0) -> dict:
    if weights is None:
        weights = dict(CIS_WEIGHTS)
    z = scored_zones.reset_index(drop=True)

    base_order = _top_order(z, _cis_from_weights(z, weights), top_n)
    base_set = set(base_order)

    rng = np.random.default_rng(seed)
    base_vec = np.array([weights[f] for f in _FACTORS], dtype=float)
    alpha = np.where(base_vec * 50.0 <= 0, 1e-3, base_vec * 50.0)

    rhos: list[float] = []
    for _ in range(n_perturbations):
        draw = rng.dirichlet(alpha)
        pw = {f: float(w) for f, w in zip(_FACTORS, draw)}
        p_order = _top_order(z, _cis_from_weights(z, pw), top_n)
        union = list(dict.fromkeys(base_order + p_order))
        b_rank = {c: i for i, c in enumerate(base_order)}
        p_rank = {c: i for i, c in enumerate(p_order)}
        fb = len(union)
        b = [b_rank.get(c, fb) for c in union]
        p = [p_rank.get(c, fb) for c in union]
        if len(set(b)) <= 1 or len(set(p)) <= 1:
            continue
        rho, _ = spearmanr(b, p)
        if rho is not None and not np.isnan(rho):
            rhos.append(float(rho))
    mean_rho = float(np.mean(rhos)) if rhos else 1.0

    jaccard: dict[str, float] = {}
    for factor in _FACTORS:
        remaining = {f: w for f, w in weights.items() if f != factor}
        total = sum(remaining.values())
        if total <= 0:
            jaccard[factor] = 0.0
            continue
        renorm = {f: w / total for f, w in remaining.items()}
        renorm[factor] = 0.0
        loo_set = set(_top_order(z, _cis_from_weights(z, renorm), top_n))
        inter = len(base_set & loo_set)
        uni = len(base_set | loo_set)
        jaccard[factor] = float(inter / uni) if uni else 1.0

    return {
        "proxy": True,
        "method": "weight_perturbation_dirichlet+leave_one_factor_out_jaccard",
        "base_weights": {f: float(w) for f, w in weights.items()},
        "n_perturbations": int(n_perturbations),
        "top_n": int(top_n),
        "weight_perturbation_mean_spearman_rho": mean_rho,
        "leave_one_out_jaccard": jaccard,
    }
