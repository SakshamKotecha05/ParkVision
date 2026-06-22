"""Streamlit-free loader for the 8 pre-built artifacts.

Used by the read-only FastAPI service (`api/main.py`) so the service never
imports streamlit. Mirrors the artifact map in `parkvision/app_data.py` but
has no caching decorator and no runtime dependency on streamlit.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from parkvision.config import ARTIFACTS

ARTIFACT_FILES: dict[str, str] = {
    "scored_zones": "scored_zones.parquet",
    "hotspots": "hotspots.parquet",
    "forecast": "forecast.parquet",
    "forecast_metrics": "forecast_metrics.json",
    "deploy_plan": "deploy_plan.parquet",
    "roi_curve": "roi_curve.parquet",
    "blind_spots": "blind_spots.parquet",
    "validation": "validation.json",
}

_BUILD_HINT = "Run `/opt/anaconda3/bin/python -m parkvision.build_artifacts` first."


def _read_parquet(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}. {_BUILD_HINT}")
    return pd.read_parquet(path)


def _read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}. {_BUILD_HINT}")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_artifacts(artifacts_dir: Path | None = None) -> dict[str, Any]:
    base = Path(artifacts_dir) if artifacts_dir is not None else ARTIFACTS
    out: dict[str, Any] = {}
    for name, filename in ARTIFACT_FILES.items():
        path = base / filename
        out[name] = _read_json(path) if filename.endswith(".json") else _read_parquet(path)
    return out


def known_zone_ids(scored_zones: pd.DataFrame) -> set[str]:
    return set(scored_zones["zone_id"].astype(str))
