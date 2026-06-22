"""Tab 5 — AI Enforcement Briefings: per-station Markdown briefings.

Reads the cached briefings/<slug>.md; if missing, generates live with the
template backend (fast/free). A 'Regenerate' button overwrites the cache.
"""
from __future__ import annotations

import streamlit as st

from parkvision import briefing


def render(data: dict) -> None:
    scored_zones = data["scored_zones"]
    forecast = data["forecast"]
    deploy_plan = data["deploy_plan"]
    blind_spots = data["blind_spots"]

    st.subheader("AI Enforcement Briefings")
    st.caption("Per-station morning briefing composed from the ranked zones, "
               "forecast, patrol plan, and blind spots. Pre-generated at build "
               "time; the live demo reads cached files (no API key required).")

    stations = sorted(scored_zones["station"].dropna().unique().tolist())
    if not stations:
        st.info("No stations available.")
        return
    station = st.selectbox("Police station", stations)

    briefing.BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = briefing.BRIEFINGS_DIR / f"{briefing.slugify(station)}.md"

    regen = st.button("Generate / Regenerate briefing")
    if regen or not cache_path.exists():
        text = briefing.make_briefing(
            station, scored_zones, forecast, deploy_plan, blind_spots)
        cache_path.write_text(text, encoding="utf-8")
        if regen:
            st.success(f"Regenerated {cache_path.name}")
    else:
        text = cache_path.read_text(encoding="utf-8")

    with st.container(key="pv-doc"):
        st.markdown(text)
