"""AI Enforcement Briefings.

Composes a readable morning-briefing Markdown for each police station from the
pre-built artifacts. The ONLY active backend is ``template`` (deterministic
f-string prose, no LLM, no API key). A future real Claude backend is a single
function replacement — see ``_generate_with_claude`` — guarded so selecting it
without the dependency fails loudly with a documented message.

Build-time: ``generate_all_briefings()`` writes briefings/<slug>.md once.
Live demo: the dashboard reads the cached .md, falling back to ``make_briefing``
(template backend is fast and free) if a file is missing.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from parkvision.config import ROOT

BRIEFING_BACKEND = "template"          # "template" (active) | "claude" (stub)
BRIEFINGS_DIR = ROOT / "briefings"


def slugify(name: str) -> str:
    """lowercase, strip punctuation, collapse whitespace to single underscores."""
    s = str(name).lower().strip()
    s = re.sub(r"[^\w\s]", "", s)        # drop punctuation (keeps word chars/spaces)
    s = re.sub(r"\s+", "_", s)           # spaces -> underscores
    return s


def _generate_with_claude(
    station: str,
    scored_zones: pd.DataFrame,
    forecast: pd.DataFrame,
    deploy_plan: pd.DataFrame,
    blind_spots: pd.DataFrame,
) -> str:
    """Future backend: real Claude-authored briefing. Intentionally unbuilt.

    Swapping to a live LLM briefing is a single function: implement this body
    (build a prompt from the same dataframes, call the Anthropic Messages API,
    return Markdown) and set ``BRIEFING_BACKEND = "claude"``.
    """
    try:
        import anthropic  # noqa: F401
    except ImportError as e:
        raise NotImplementedError(
            "anthropic package not installed — set up ANTHROPIC_API_KEY and "
            "`pip install anthropic`, then implement _generate_with_claude."
        ) from e
    raise NotImplementedError(
        "Claude briefing backend not implemented yet — implement "
        "_generate_with_claude and remove this raise."
    )


def _generate_with_template(
    station: str,
    scored_zones: pd.DataFrame,
    forecast: pd.DataFrame,
    deploy_plan: pd.DataFrame,
    blind_spots: pd.DataFrame,
) -> str:
    """Deterministic Markdown briefing composed from the dataframes."""
    sz = scored_zones[scored_zones["station"] == station].sort_values(
        "cis", ascending=False)
    if sz.empty:
        return (f"# Morning Enforcement Briefing — {station}\n\n"
                f"No scored zones are currently attributed to {station}.\n")

    top = sz.head(3)
    total_high = int(sz["high_impact"].sum())
    n_zones = len(sz)

    lines: list[str] = []
    lines.append(f"# Morning Enforcement Briefing — {station}")
    lines.append("")
    lead = top.iloc[0]
    lines.append(
        f"Good morning. {station} has {n_zones} ranked zone(s) carrying "
        f"{total_high} high-impact (flow-choking) violations. Today's top "
        f"chokepoint is zone {lead['zone_id']} (CIS {lead['cis']:.1f}, "
        f"{int(lead['high_impact'])} high-impact, {int(lead['n_violations'])} "
        f"total violations).")
    lines.append("")

    lines.append("## Priority zones")
    for _, r in top.iterrows():
        lines.append(
            f"- **Zone {r['zone_id']}** — CIS {r['cis']:.1f}, "
            f"{int(r['high_impact'])} high-impact of "
            f"{int(r['n_violations'])} violations.")
    lines.append("")

    # Rising zones in this station (from forecast.rising)
    station_ids = set(sz["zone_id"])
    rising = forecast[(forecast["zone_id"].isin(station_ids))
                      & (forecast["rising"] == True)]  # noqa: E712
    if not rising.empty:
        rising = rising.sort_values("risk", ascending=False)
        names = ", ".join(rising["zone_id"].astype(str).tolist())
        lines.append("## Rising risk")
        lines.append(
            f"Watch {len(rising)} zone(s) trending up: {names}. "
            "Forecast risk is climbing here — pre-empt before it peaks.")
        lines.append("")

    # Deploy-plan zones that fall in this station
    plan_here = deploy_plan[deploy_plan["zone_id"].isin(station_ids)]
    if not plan_here.empty:
        plan_here = plan_here.sort_values("rank")
        ranks = ", ".join(f"#{int(r)} ({z})" for r, z in
                          zip(plan_here["rank"], plan_here["zone_id"]))
        lines.append("## On today's patrol plan")
        lines.append(
            f"{len(plan_here)} of your zones are in the recommended patrol "
            f"deployment: {ranks}. These are the highest-leverage stops.")
        lines.append("")

    # Blind spots in this station
    bs_here = blind_spots[blind_spots["station"] == station]
    if not bs_here.empty:
        bs_here = bs_here.sort_values("blindspot_rank")
        names = ", ".join(bs_here["zone_id"].astype(str).tolist())
        lines.append("## Blind spots")
        lines.append(
            f"{len(bs_here)} under-served high-impact zone(s) need attention: "
            f"{names}. High real-flow cost, historically under-patrolled — "
            "cheap wins.")
        lines.append("")

    lines.append("---")
    lines.append("*Generated by ParkVision (template backend). "
                 "Ranking by Congestion-Impact Score (CIS).*")
    return "\n".join(lines)


def make_briefing(
    station: str,
    scored_zones: pd.DataFrame,
    forecast: pd.DataFrame,
    deploy_plan: pd.DataFrame,
    blind_spots: pd.DataFrame,
    backend: str | None = None,
) -> str:
    """Return a Markdown briefing for ``station``. Default backend = template."""
    chosen = backend or BRIEFING_BACKEND
    if chosen == "claude":
        return _generate_with_claude(
            station, scored_zones, forecast, deploy_plan, blind_spots)
    if chosen == "template":
        return _generate_with_template(
            station, scored_zones, forecast, deploy_plan, blind_spots)
    raise ValueError(f"Unknown briefing backend: {chosen!r}")


def generate_all_briefings(
    out_dir: Path | None = None,
    scored_zones: pd.DataFrame | None = None,
    forecast: pd.DataFrame | None = None,
    deploy_plan: pd.DataFrame | None = None,
    blind_spots: pd.DataFrame | None = None,
) -> list[Path]:
    """Write briefings/<slug>.md for every distinct station; return paths.

    If dataframes are omitted, loads them from artifacts via app_data. Pass
    them explicitly in tests to avoid touching disk artifacts.
    """
    out = Path(out_dir) if out_dir is not None else BRIEFINGS_DIR
    out.mkdir(parents=True, exist_ok=True)

    if scored_zones is None:
        from parkvision import app_data
        scored_zones = app_data.load_scored_zones()
        forecast = app_data.load_forecast()
        deploy_plan = app_data.load_deploy_plan()
        blind_spots = app_data.load_blind_spots()

    written: list[Path] = []
    for station in sorted(scored_zones["station"].dropna().unique()):
        text = make_briefing(
            station, scored_zones, forecast, deploy_plan, blind_spots)
        path = out / f"{slugify(station)}.md"
        path.write_text(text, encoding="utf-8")
        written.append(path)
    return written
