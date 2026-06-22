import numpy as np
import pandas as pd
from parkvision import sensitivity
from parkvision.config import CIS_WEIGHTS


def _toy_scored():
    rng = np.random.default_rng(0)
    n = 80
    comp = {f"c_{k}": rng.random(n) for k in CIS_WEIGHTS}
    df = pd.DataFrame(comp)
    df["zone_id"] = [f"z{i}" for i in range(n)]
    df["cis"] = 100 * sum(CIS_WEIGHTS[k] * df[f"c_{k}"] for k in CIS_WEIGHTS)
    return df


def test_report_shape_and_json_safe():
    rep = sensitivity.sensitivity_report(_toy_scored(), n_perturbations=20, top_n=10, seed=0)
    assert rep["proxy"] is True
    assert set(rep["base_weights"]) == set(CIS_WEIGHTS)
    assert 0.0 <= rep["weight_perturbation_mean_spearman_rho"] <= 1.0
    assert set(rep["leave_one_out_jaccard"]) == set(CIS_WEIGHTS)
    import json
    json.dumps(rep)  # must not raise (native types only)


def test_report_is_deterministic():
    z = _toy_scored()
    a = sensitivity.sensitivity_report(z, n_perturbations=20, top_n=10, seed=0)
    b = sensitivity.sensitivity_report(z, n_perturbations=20, top_n=10, seed=0)
    assert a == b
