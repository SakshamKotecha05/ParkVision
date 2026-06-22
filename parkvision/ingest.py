import ast
import re
import pandas as pd
from .config import DATA_PATH, IST, BBOX

_ARTERIAL = re.compile(r"highway|ring road|flyover|elevated|expressway|nice road|underpass|\bnh[\s-]?\d")
_MAIN     = re.compile(r"main road|main rd|\bmain\b")
_CROSS    = re.compile(r"\bcross\b")
_ROAD     = re.compile(r"\broad\b|\brd\b|\bstreet\b|\bst\b|marg|avenue")
_RESID    = re.compile(r"layout|nagar|colony|block|extension|garden|puram|pura\b|town|circle|stage")

_KEEP = ["id", "latitude", "longitude", "violation", "vehicle_type",
         "junction_name", "road_type", "police_station", "validation_status",
         "dt_ist", "hour", "dow", "date", "created_by_id", "device_id",
         "vehicle_number"]

def parse_violation_types(raw) -> list[str]:
    if not isinstance(raw, str):
        return []
    try:
        val = ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        return []
    return [str(x).strip() for x in val] if isinstance(val, list) else []

def classify_road_type(location) -> str:
    """Classify the road class from the first segment of a `location` address string."""
    if not isinstance(location, str) or not location.strip():
        return "unknown"
    s = location.split(",")[0].lower().strip()
    if _ARTERIAL.search(s): return "arterial"
    if _MAIN.search(s):     return "main"
    if _CROSS.search(s):    return "cross"
    if _ROAD.search(s):     return "road"
    if _RESID.search(s):    return "residential"
    return "unknown"

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
    df = df[df["dt_ist"].notna()]

    if "location" in df.columns:
        df["road_type"] = df["location"].apply(classify_road_type)
    else:
        df["road_type"] = "unknown"

    if "created_by_id" not in df.columns:
        df["created_by_id"] = "unknown"

    if "device_id" not in df.columns:
        df["device_id"] = "unknown"

    if "vehicle_number" not in df.columns:
        df["vehicle_number"] = "unknown"

    m = (df["latitude"].between(BBOX["lat_min"], BBOX["lat_max"]) &
         df["longitude"].between(BBOX["lon_min"], BBOX["lon_max"]))
    df = df[m].reset_index(drop=True)
    return df[_KEEP]
