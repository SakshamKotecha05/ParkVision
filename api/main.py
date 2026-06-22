"""api/main.py — ParkVision read-only serving layer.

Stateless, read-only HTTP service over the 8 precomputed artifacts. Loads
them ONCE at startup via a FastAPI lifespan into app.state; every handler
reads in-memory frames only — no per-request disk I/O, no streamlit, no
model, no raw rows. Mirrors the security posture of the sibling ParkSight
API: CORS allow-list (never "*"), generic 500 with no traceback/path leak,
Pydantic Query bounds, fail-closed 404 for unknown zone ids, debug=False.
Responses are zone-level aggregates only — no PII.
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from parkvision import artifact_store

API_VERSION = "0.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.artifacts_loaded = False
    data = artifact_store.load_artifacts()
    for key, value in data.items():
        setattr(app.state, key, value)
    app.state.known_zone_ids = artifact_store.known_zone_ids(data["scored_zones"])
    app.state.artifacts_loaded = True
    yield


app = FastAPI(lifespan=lifespan, debug=False)

_DEFAULT_CORS_ORIGINS = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "https://share.streamlit.io",
]
_cors_env = os.environ.get("PARKVISION_CORS_ORIGINS", "")
_cors_origins = (
    [o.strip() for o in _cors_env.split(",") if o.strip()]
    if _cors_env else _DEFAULT_CORS_ORIGINS
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Never echo str(exc) / traceback / filesystem path — generic JSON only.
    HTTPException (404/422) is handled by FastAPI's own default handler."""
    return JSONResponse(status_code=500, content={"detail": "internal error"})


def _to_native(value):
    return value.item() if hasattr(value, "item") else value


def _rows(df, native_cols):
    return [
        {c: _to_native(row[c]) for c in native_cols}
        for _, row in df.iterrows()
    ]


class HealthResponse(BaseModel):
    status: str
    artifacts_loaded: bool
    version: str


@app.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    loaded = bool(getattr(request.app.state, "artifacts_loaded", False))
    return HealthResponse(
        status="ok" if loaded else "degraded",
        artifacts_loaded=loaded,
        version=API_VERSION,
    )


from typing import Optional
from fastapi import HTTPException, Query


class ZoneRow(BaseModel):
    zone_id: str
    lat: float
    lon: float
    cis: float
    high_impact: int
    n_violations: int
    station: Optional[str] = None


class HotspotRow(BaseModel):
    hotspot_id: int
    total_cis: float
    mean_cis: float
    n_zones: int
    lat: float
    lon: float


_ZONE_COLS = ["zone_id", "lat", "lon", "cis", "high_impact", "n_violations", "station"]
_HOTSPOT_COLS = ["hotspot_id", "total_cis", "mean_cis", "n_zones", "lat", "lon"]


@app.get("/zones", response_model=list[ZoneRow])
def get_zones(
    request: Request,
    top_n: int = Query(default=20, ge=1, le=500),
    min_cis: float = Query(default=0.0, ge=0.0, le=100.0),
    station: Optional[str] = None,
    zone_id: Optional[str] = None,
) -> list[ZoneRow]:
    df = request.app.state.scored_zones

    if zone_id is not None:
        if zone_id not in request.app.state.known_zone_ids:
            raise HTTPException(status_code=404, detail="unknown zone_id")
        rows = df[df["zone_id"].astype(str) == zone_id]
        return [ZoneRow(**r) for r in _rows(rows[_ZONE_COLS], _ZONE_COLS)]

    view = df[df["cis"] >= min_cis]
    if station is not None:
        view = view[view["station"] == station]
    view = view.sort_values("cis", ascending=False).head(top_n)
    return [ZoneRow(**r) for r in _rows(view[_ZONE_COLS], _ZONE_COLS)]


@app.get("/hotspots", response_model=list[HotspotRow])
def get_hotspots(
    request: Request,
    top_n: int = Query(default=10, ge=1, le=50),
) -> list[HotspotRow]:
    df = request.app.state.hotspots.sort_values("total_cis", ascending=False).head(top_n)
    return [HotspotRow(**r) for r in _rows(df[_HOTSPOT_COLS], _HOTSPOT_COLS)]


RECOMMENDED_K = 25  # parkvision.deploy.recommend_k on the full data


class ForecastRow(BaseModel):
    zone_id: str
    risk: float
    slope: float
    rising: bool


class DeployPlanRow(BaseModel):
    rank: int
    zone_id: str
    lat: float
    lon: float
    cis: float
    high_impact_covered: float
    n_zones_covered: int


class DeployPlanResponse(BaseModel):
    plan: list[DeployPlanRow]
    recommended_k: int
    coverage_pct_at_k20: Optional[float] = None


class BlindSpotRow(BaseModel):
    blindspot_rank: int
    zone_id: str
    lat: float
    lon: float
    cis: float
    high_impact: int
    n_violations: int
    station: Optional[str] = None


class ValidationResponse(BaseModel):
    top_n: int
    overlap_pct: float
    n_top_zones: int


_FORECAST_COLS = ["zone_id", "risk", "slope", "rising"]
_DEPLOY_COLS = ["rank", "zone_id", "lat", "lon", "cis", "high_impact_covered", "n_zones_covered"]
_BLIND_COLS = ["blindspot_rank", "zone_id", "lat", "lon", "cis", "high_impact", "n_violations", "station"]


@app.get("/forecast", response_model=list[ForecastRow])
def get_forecast(
    request: Request,
    top_n: int = Query(default=20, ge=1, le=500),
    rising_only: bool = False,
) -> list[ForecastRow]:
    df = request.app.state.forecast
    if rising_only:
        df = df[df["rising"] == True]  # noqa: E712
    df = df.sort_values("risk", ascending=False).head(top_n)
    return [ForecastRow(**r) for r in _rows(df[_FORECAST_COLS], _FORECAST_COLS)]


@app.get("/deploy-plan", response_model=DeployPlanResponse)
def get_deploy_plan(request: Request) -> DeployPlanResponse:
    plan_df = request.app.state.deploy_plan.sort_values("rank")
    roi = request.app.state.roi_curve
    k20 = roi.loc[roi["k"] == 20, "covered_pct"]
    coverage = float(k20.iloc[0]) if not k20.empty else None
    plan_rows = [DeployPlanRow(**r) for r in _rows(plan_df[_DEPLOY_COLS], _DEPLOY_COLS)]
    return DeployPlanResponse(
        plan=plan_rows, recommended_k=RECOMMENDED_K, coverage_pct_at_k20=coverage,
    )


@app.get("/blind-spots", response_model=list[BlindSpotRow])
def get_blind_spots(request: Request) -> list[BlindSpotRow]:
    df = request.app.state.blind_spots.sort_values("blindspot_rank")
    return [BlindSpotRow(**r) for r in _rows(df[_BLIND_COLS], _BLIND_COLS)]


@app.get("/validation", response_model=ValidationResponse)
def get_validation(request: Request) -> ValidationResponse:
    return ValidationResponse(**request.app.state.validation)
