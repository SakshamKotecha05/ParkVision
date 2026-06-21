"""Tab 4 — Enforcement Blind Spots: under-served high-impact zones."""
from __future__ import annotations

import pandas as pd
import pydeck as pdk
import streamlit as st

from parkvision.dashboard import theme

# Source: EDA lock — top-10 busiest stations hold 58.6% of enforcement effort.
TOP10_STATION_SKEW_PCT = 58.6


def render(data: dict) -> None:
    blind: pd.DataFrame = data["blind_spots"]

    st.subheader("Enforcement Blind Spots")
    st.markdown(
        f"""
        <div class="pv-headline">
          <span class="big">{TOP10_STATION_SKEW_PCT:.1f}%</span>
          <span class="sub">of all logged enforcement effort sits with the
          top-10 busiest stations. These zones sit outside that coverage —
          high CIS, high real-flow cost, under-patrolled. The cheapest
          wins on the board.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if blind.empty:
        st.info("No blind spots in the current artifact.")
        return

    c1, c2 = st.columns(2)
    c1.metric("Blind-spot zones", f"{len(blind):,}")
    c2.metric("High-impact in blind spots",
              f"{int(blind['high_impact'].sum()):,}")

    st.markdown('<hr class="pv-rule">', unsafe_allow_html=True)
    map_df = blind[["lat", "lon", "zone_id", "cis", "high_impact",
                    "station"]].copy()
    map_df["color"] = [theme.WARN_RGBA] * len(map_df)
    layer = pdk.Layer(
        "ScatterplotLayer", map_df,
        get_position=["lon", "lat"], get_radius=180,
        get_fill_color="color", pickable=True)
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(
            latitude=float(map_df["lat"].mean()),
            longitude=float(map_df["lon"].mean()), zoom=10),
        map_style=None,
        tooltip={"text": "Zone {zone_id}\nCIS {cis}\n{station}"}))

    st.markdown("##### Blind-spot zones")
    show = blind[["blindspot_rank", "zone_id", "station", "cis",
                  "high_impact", "n_violations"]].rename(
        columns={"blindspot_rank": "rank", "cis": "CIS",
                 "high_impact": "high-impact", "n_violations": "violations"})
    st.dataframe(show, hide_index=True, use_container_width=True)
