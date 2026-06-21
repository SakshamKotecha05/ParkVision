import json
import math
from pathlib import Path
import pandas as pd
from . import ingest, cis, hotspots, validate, forecast, deploy
from .config import ARTIFACTS, DATA_PATH

_FC_COLS = ["zone_id", "risk", "slope", "rising"]
_FRAMING = ("Enforcement-pattern forecast, not a congestion clock: created_datetime is "
            "enforcement-logging time, synthetic below the hour (spec §11).")


def _json_safe(d):
    return {k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in d.items()}


def _forecast_frame(violations, when):
    """Per-zone next-window risk + trend; empty-but-schema'd if panel too small to train."""
    panel = forecast.build_panel(violations)
    trend = forecast.zone_trend(violations)
    if panel.empty:
        return pd.DataFrame(columns=_FC_COLS), {"spearman": float("nan"), "mae": float("nan"),
                                                "n_zones_valid": 0, "framing": _FRAMING}
    static = forecast.zone_static_features(violations)
    history = panel.merge(static[["zone_id", "morning_share"]], on="zone_id", how="left")
    model = forecast.train_forecaster(history)
    feats = forecast.latest_zone_features(panel, static)
    risk = forecast.predict_risk(model, feats, when=when)
    fc = (risk.merge(trend, on="zone_id", how="left")
              .fillna({"slope": 0.0, "rising": False}))
    fc["rising"] = fc["rising"].astype(bool)
    metrics = {**forecast.backtest(violations), "framing": _FRAMING}
    return fc[_FC_COLS], metrics


def build(out_dir=ARTIFACTS, data_path=DATA_PATH) -> dict:
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)

    violations = ingest.load_violations(data_path)
    zones = cis.score_zones(violations)
    zones_h = hotspots.detect_hotspots(zones)
    val = validate.junction_overlap(zones_h)

    when = forecast._period(violations).max()
    fc, metrics = _forecast_frame(violations, when=when)
    plan, stats = deploy.plan_deployment(zones, k=20)
    curve = deploy.roi_curve(zones)
    rec_k = deploy.recommend_k(curve)
    blind = validate.blind_spots(zones)

    zones_h.to_parquet(out / "scored_zones.parquet", index=False)
    hotspots.rank_hotspots(zones_h, top_n=50).to_parquet(out / "hotspots.parquet", index=False)
    (out / "validation.json").write_text(json.dumps(val, indent=2))
    fc.to_parquet(out / "forecast.parquet", index=False)
    (out / "forecast_metrics.json").write_text(json.dumps(_json_safe(metrics), indent=2, allow_nan=False))
    plan.to_parquet(out / "deploy_plan.parquet", index=False)
    curve.to_parquet(out / "roi_curve.parquet", index=False)
    blind.to_parquet(out / "blind_spots.parquet", index=False)

    return {"n_zones": int(len(zones_h)),
            "top_cis": float(zones_h["cis"].max()) if len(zones_h) else 0.0,
            "overlap_pct": val["overlap_pct"],
            "spearman": metrics["spearman"],
            "covered_pct": stats["covered_pct"],
            "efficiency": stats["efficiency"],
            "recommended_k": int(rec_k)}


if __name__ == "__main__":
    print(build())
