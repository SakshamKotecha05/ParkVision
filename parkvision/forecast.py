"""Per-zone enforcement-pattern forecast.

NOTE (spec §11): created_datetime is enforcement-logging time, anonymization-
synthesized below the hour. This model predicts *enforcement-pattern* risk
(where violations will keep being logged), NOT a live congestion clock. The
only time signals used are day-of-week and a per-zone morning-enforcement share.
All features are leakage-safe: lags are shifted into the past; static features
are computed from the training window only (see `zone_static_features(before=)`).
"""
import numpy as np
import pandas as pd
import lightgbm as lgb
from scipy.stats import spearmanr
from .config import severity_weight, PEAK_HOURS_IST
from .cis import assign_zone

FEATURES = ["lat", "lon", "dow", "roll7", "roll28", "morning_share"]
_PANEL_COLS = ["zone_id", "period", "lat", "lon", "dow", "n", "risk", "roll7", "roll28"]


def _period(violations):
    return pd.to_datetime(violations["dt_ist"]).dt.tz_localize(None).dt.normalize()


def build_panel(violations, min_total=5):
    df = assign_zone(violations)
    df["sev"] = df["violation"].map(severity_weight)
    df["period"] = _period(df)
    df = df.dropna(subset=["period"])

    counts = df.groupby("zone_id")["sev"].transform("size")
    df = df[counts >= min_total]
    if df.empty:
        return pd.DataFrame(columns=_PANEL_COLS)

    daily = (df.groupby(["zone_id", "period"])
               .agg(risk=("sev", "sum"), n=("sev", "size"),
                    lat=("latitude", "mean"), lon=("longitude", "mean"))
               .reset_index()
               .sort_values(["zone_id", "period"]))
    daily["dow"] = daily["period"].dt.dayofweek
    g = daily.groupby("zone_id")["risk"]
    daily["roll7"] = g.transform(lambda s: s.shift(1).rolling(7, min_periods=1).mean())
    daily["roll28"] = g.transform(lambda s: s.shift(1).rolling(28, min_periods=1).mean())
    daily[["roll7", "roll28"]] = daily[["roll7", "roll28"]].fillna(0.0)
    return daily[_PANEL_COLS].reset_index(drop=True)


def zone_static_features(violations, before=None):
    df = violations.copy()
    df = assign_zone(df)
    if before is not None:
        df = df[_period(df) <= pd.Timestamp(before)]
    df["is_morning"] = df["hour"].isin(PEAK_HOURS_IST)
    out = (df.groupby("zone_id")
             .agg(morning_share=("is_morning", "mean"), total_n=("is_morning", "size"))
             .reset_index())
    return out


def train_forecaster(history, target="risk"):
    model = lgb.LGBMRegressor(
        n_estimators=300, learning_rate=0.05, num_leaves=31,
        min_child_samples=20, subsample=0.8, subsample_freq=1,
        colsample_bytree=0.9, random_state=42, n_jobs=-1, verbose=-1,
    )
    model.fit(history[FEATURES], history[target])
    return model


def latest_zone_features(panel, static):
    if panel.empty:
        return pd.DataFrame(columns=["zone_id", "lat", "lon", "roll7", "roll28", "morning_share"])
    last = (panel.sort_values("period")
                 .groupby("zone_id")
                 .tail(1)[["zone_id", "lat", "lon", "roll7", "roll28"]])
    return last.merge(static[["zone_id", "morning_share"]], on="zone_id", how="left").reset_index(drop=True)


def predict_risk(model, zones, when):
    z = zones.copy()
    z["dow"] = pd.Timestamp(when).dayofweek
    pred = np.clip(model.predict(z[FEATURES]), 0.0, None)
    return pd.DataFrame({"zone_id": z["zone_id"].to_numpy(), "risk": pred})


def backtest(violations, train_end="2024-02-29", valid_end="2024-03-31", min_total=5):
    train_end, valid_end = pd.Timestamp(train_end), pd.Timestamp(valid_end)
    panel = build_panel(violations, min_total=min_total)
    static = zone_static_features(violations, before=train_end)        # leak-safe: train-only
    panel = panel.merge(static[["zone_id", "morning_share"]], on="zone_id", how="left")

    train = panel[panel["period"] <= train_end]
    valid = panel[(panel["period"] > train_end) & (panel["period"] <= valid_end)]
    meta = {"n_train": int(len(train)), "n_valid": int(len(valid)),
            "train_end": str(train_end.date()), "valid_end": str(valid_end.date())}
    if train.empty or valid.empty:
        return {"spearman": float("nan"), "mae": float("nan"), "n_zones_valid": 0, **meta}

    model = train_forecaster(train)
    valid = valid.copy()
    valid["pred"] = np.clip(model.predict(valid[FEATURES]), 0.0, None)
    agg = valid.groupby("zone_id").agg(pred=("pred", "sum"), actual=("risk", "sum"))
    rho = float(spearmanr(agg["pred"], agg["actual"]).statistic) if len(agg) > 1 else float("nan")
    mae = float((valid["pred"] - valid["risk"]).abs().mean())
    return {"spearman": rho, "mae": mae, "n_zones_valid": int(len(agg)), **meta}


def zone_trend(violations, min_weeks=3):
    df = assign_zone(violations)
    df["sev"] = df["violation"].map(severity_weight)
    df["week"] = _period(df).dt.to_period("W").dt.start_time
    df = df.dropna(subset=["week"])
    weekly = df.groupby(["zone_id", "week"])["sev"].sum().reset_index(name="risk")

    out = []
    for zid, grp in weekly.groupby("zone_id"):
        g = grp.sort_values("week")
        if len(g) < min_weeks:
            out.append({"zone_id": zid, "slope": 0.0, "rising": False})
            continue
        x = np.arange(len(g), dtype=float)
        slope = float(np.polyfit(x, g["risk"].to_numpy(dtype=float), 1)[0])
        out.append({"zone_id": zid, "slope": slope, "rising": bool(slope > 1e-9)})
    return pd.DataFrame(out, columns=["zone_id", "slope", "rising"])
