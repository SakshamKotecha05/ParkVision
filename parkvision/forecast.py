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
    daily["roll7"] = (g.shift(1).rolling(7, min_periods=1).mean()
                       .reset_index(level=0, drop=True))
    daily["roll28"] = (g.shift(1).rolling(28, min_periods=1).mean()
                        .reset_index(level=0, drop=True))
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
