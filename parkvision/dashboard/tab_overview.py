"""Tab 1 — Priority Zones: headline stats, CIS map, top-20 table, filters."""
from __future__ import annotations

import pandas as pd
import pydeck as pdk
import streamlit as st

from parkvision.dashboard import theme

# Source: EDA lock (Plan 1 hour-distribution / config.PEAK_HOURS_IST analysis block).
# Only ~9.2% of all ~298,450 violations are flow-choking (high-impact).
# NOT in artifacts — fixed historical fact, do not recompute.
FLOW_CHOKING_PCT = 9.2
TOTAL_VIOLATIONS = 298_450


def render(data: dict) -> None:
    zones: pd.DataFrame = data["scored_zones"]
    forecast: pd.DataFrame = data["forecast"]
    validation: dict = data["validation"]

    n_zones = len(zones)
    top_cis = float(zones["cis"].iloc[0]) if n_zones else 0.0
    overlap = float(validation.get("overlap_pct", 0.0))

    st.subheader("Priority Zones")
    st.markdown(
        f"""
        <div class="pv-headline">
          <span class="big">{FLOW_CHOKING_PCT:.1f}%</span>
          <span class="sub">of {TOTAL_VIOLATIONS:,} logged violations actually
          choke traffic flow. ParkVision ranks the {n_zones:,} zones so
          enforcement hits the few that matter.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Scored zones", f"{n_zones:,}")
    c2.metric("Top zone CIS", f"{top_cis:.1f}")
    c3.metric("Junction-overlap proof", f"{overlap:.1f}%",
              help="Share of top zones that sit on a real road junction — "
                   "independent geometric validation of the CIS ranking.")

    # --- Filters ---
    st.markdown('<hr class="pv-rule">', unsafe_allow_html=True)
    st.markdown("##### Filters")
    f1, f2, f3 = st.columns([2, 2, 1])
    stations = sorted(zones["station"].dropna().unique().tolist())
    picked = f1.multiselect("Police station", stations, default=[])
    cis_min = f2.slider("Minimum CIS", 0.0, float(zones["cis"].max()),
                        0.0, step=1.0)
    rising_only = f3.checkbox("Rising only", value=False)

    view = zones
    if picked:
        view = view[view["station"].isin(picked)]
    view = view[view["cis"] >= cis_min]
    if rising_only:
        rising_ids = set(forecast.loc[forecast["rising"] == True, "zone_id"])  # noqa: E712
        view = view[view["zone_id"].isin(rising_ids)]

    if view.empty:
        st.info("No zones match the current filters.")
        return

    # --- Map ---
    cis_max = float(view["cis"].max())
    map_df = view[["lat", "lon", "cis", "zone_id", "station",
                   "high_impact"]].copy()
    map_df["color"] = map_df["cis"].apply(
        lambda c: theme.cis_to_color(c, cis_max))
    map_df["radius"] = 40 + (map_df["cis"] / cis_max) * 220

    layer = pdk.Layer(
        "ScatterplotLayer",
        map_df,
        get_position=["lon", "lat"],
        get_radius="radius",
        get_fill_color="color",
        pickable=True,
    )
    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=pdk.ViewState(
                latitude=float(map_df["lat"].mean()),
                longitude=float(map_df["lon"].mean()),
                zoom=10, pitch=0),
            map_style=None,
            tooltip={"text": "Zone {zone_id}\nCIS {cis}\n{station}\n"
                             "high-impact {high_impact}"},
        )
    )

    # --- Top-20 table ---
    st.markdown("##### Top 20 priority zones")
    top = (view.sort_values("cis", ascending=False)
                .head(20)[["zone_id", "station", "cis", "high_impact",
                           "n_violations"]]
                .rename(columns={"cis": "CIS",
                                 "high_impact": "high-impact",
                                 "n_violations": "violations"}))
    st.dataframe(top, hide_index=True, use_container_width=True)
