"""Cached loader for the 9 pre-built artifacts in ``artifacts/``.

Plan 3 is read-only: this module never regenerates artifacts, it only reads
them. Public accessors are wrapped in ``st.cache_data`` so the Streamlit app
re-reads disk only once per session; the private ``_read_*`` helpers are
cache-free and runtime-independent for testing.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from parkvision.config import ARTIFACTS  # ARTIFACTS == ROOT / "artifacts"

# logical name -> filename on disk
ARTIFACT_FILES: dict[str, str] = {
    "scored_zones": "scored_zones.parquet",
    "hotspots": "hotspots.parquet",
    "forecast": "forecast.parquet",
    "forecast_metrics": "forecast_metrics.json",
    "deploy_plan": "deploy_plan.parquet",
    "roi_curve": "roi_curve.parquet",
    "blind_spots": "blind_spots.parquet",
    "validation": "validation.json",
    "cis_sensitivity": "cis_sensitivity.json",
}

_BUILD_HINT = (
    "Run `/opt/anaconda3/bin/python -m parkvision.build_artifacts` first."
)


def _read_parquet(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}. {_BUILD_HINT}")
    return pd.read_parquet(path)


def _read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}. {_BUILD_HINT}")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


@st.cache_data
def load_scored_zones() -> pd.DataFrame:
    return _read_parquet(ARTIFACTS / ARTIFACT_FILES["scored_zones"])


@st.cache_data
def load_hotspots() -> pd.DataFrame:
    return _read_parquet(ARTIFACTS / ARTIFACT_FILES["hotspots"])


@st.cache_data
def load_forecast() -> pd.DataFrame:
    return _read_parquet(ARTIFACTS / ARTIFACT_FILES["forecast"])


@st.cache_data
def load_forecast_metrics() -> dict:
    return _read_json(ARTIFACTS / ARTIFACT_FILES["forecast_metrics"])


@st.cache_data
def load_deploy_plan() -> pd.DataFrame:
    return _read_parquet(ARTIFACTS / ARTIFACT_FILES["deploy_plan"])


@st.cache_data
def load_roi_curve() -> pd.DataFrame:
    return _read_parquet(ARTIFACTS / ARTIFACT_FILES["roi_curve"])


@st.cache_data
def load_blind_spots() -> pd.DataFrame:
    return _read_parquet(ARTIFACTS / ARTIFACT_FILES["blind_spots"])


@st.cache_data
def load_validation() -> dict:
    return _read_json(ARTIFACTS / ARTIFACT_FILES["validation"])


@st.cache_data
def load_cis_sensitivity() -> dict:
    return _read_json(ARTIFACTS / ARTIFACT_FILES["cis_sensitivity"])


@st.cache_data
def load_all() -> dict[str, Any]:
    """Return all 8 artifacts keyed by logical name."""
    return {
        "scored_zones": load_scored_zones(),
        "hotspots": load_hotspots(),
        "forecast": load_forecast(),
        "forecast_metrics": load_forecast_metrics(),
        "deploy_plan": load_deploy_plan(),
        "roi_curve": load_roi_curve(),
        "blind_spots": load_blind_spots(),
        "validation": load_validation(),
        "cis_sensitivity": load_cis_sensitivity(),
    }
