import ast
import pandas as pd
from .config import DATA_PATH, IST, BBOX

_KEEP = ["id", "latitude", "longitude", "violation", "vehicle_type",
         "junction_name", "police_station", "validation_status",
         "dt_ist", "hour", "dow", "date"]

def parse_violation_types(raw) -> list[str]:
    if not isinstance(raw, str):
        return []
    try:
        val = ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        return []
    return [str(x).strip() for x in val] if isinstance(val, list) else []

def load_violations(path=DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    df["violation"] = df["violation_type"].apply(parse_violation_types)
    df = df.explode("violation", ignore_index=True)
    df = df[df["violation"].notna()]

    ts = pd.to_datetime(df["created_datetime"], errors="coerce", utc=True).dt.tz_convert(IST)
    df["dt_ist"] = ts
    df["hour"] = ts.dt.hour
    df["dow"] = ts.dt.dayofweek
    df["date"] = ts.dt.date

    m = (df["latitude"].between(BBOX["lat_min"], BBOX["lat_max"]) &
         df["longitude"].between(BBOX["lon_min"], BBOX["lon_max"]))
    df = df[m].reset_index(drop=True)
    return df[_KEEP]
