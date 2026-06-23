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

# Source: docs/EDA_RECHECK_2026-06-22.md ("9.1% of records come from vehicles
# seen >=5 times"). NOT in artifacts — fixed historical fact, do not recompute.
REPEAT_OFFENDER_PCT = 9.1

# Source: raw CSV `data_sent_to_scita` column, verified 2026-06-22:
# 255,893 of 298,450 records (85.7%) already flow into BTP's existing SCITA pipeline.
# NOT in artifacts — fixed historical fact, do not recompute.
SCITA_PCT = 85.7


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

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Scored zones", f"{n_zones:,}")
    c2.metric("Top zone CIS", f"{top_cis:.1f}")
    c3.metric("Junction-overlap proof", f"{overlap:.1f}%",
              help="Share of top zones that sit on a real road junction — "
                   "independent geometric validation of the CIS ranking.")
    with c3:
        st.markdown(
            '<span class="pv-verified">Verified</span>',
            unsafe_allow_html=True,
        )

    if "single_source" in zones.columns:
        top20_div = zones.sort_values("cis", ascending=False).head(20)
        multi_source_pct = float((~top20_div["single_source"]).mean() * 100)
        c4.metric("Multi-source", f"{multi_source_pct:.0f}%",
                  help="Share of top-20 zones whose violations come from "
                       "≥2 distinct officers — independent proof hotspots "
                       "aren't one officer's patrol beat.")
        with c4:
            st.markdown(
                '<span class="pv-verified">Verified</span>',
                unsafe_allow_html=True,
            )

    st.caption(
        f"{REPEAT_OFFENDER_PCT:.1f}% of all violations come from vehicles seen "
        "5+ times across the dataset — these top zones aren't just busy, some "
        "are chronic repeat-offender locations (a descriptive pattern, not "
        "another validation proof)."
    )
    st.caption(
        f"{SCITA_PCT:.1f}% of all violations already flow into BTP's SCITA "
        "pipeline — ParkVision is a scoring layer on data they already "
        "route, not a new system to adopt."
    )

    sens: dict = data["cis_sensitivity"]
    rho = float(sens["weight_perturbation_mean_spearman_rho"])
    jaccard: dict = sens["leave_one_out_jaccard"]

    with st.expander("How sensitive is the ranking to our weights?"):
        st.metric(
            "Weight robustness (Spearman ρ)", f"{rho:.2f}",
            help="Mean rank correlation between the top-20 ranking under the "
                 "chosen CIS weights and the ranking under 100 randomized "
                 "weight draws. Closer to 1.0 = more robust to the exact "
                 "weights chosen.",
        )
        if rho >= 0.8:
            st.caption(
                "The top-zone ranking is robust to the exact CIS weights — "
                "randomizing the weight mix still recovers nearly the same "
                "priority list."
            )
        else:
            st.caption(
                "The top-zone ranking is stable within the high-impact band, "
                "but the exact ordering shifts with the weights — which is "
                "why we also validate against real BTP junctions."
            )
        jac_df = (
            pd.DataFrame({"factor": list(jaccard.keys()),
                          "leave-one-out overlap": list(jaccard.values())})
            .sort_values("leave-one-out overlap")
            .reset_index(drop=True)
        )
        st.caption(
            "Leave-one-out overlap: how much the top-20 list changes if a "
            "factor is dropped and the rest re-normalized. Lower = that "
            "factor matters more to the ranking."
        )
        st.dataframe(jac_df, hide_index=True, width="stretch")

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
    _top20_cols = ["zone_id", "station", "cis", "high_impact", "n_violations"]
    _rename = {"cis": "CIS", "high_impact": "high-impact",
               "n_violations": "violations"}
    if "single_source" in view.columns:
        _top20_cols.append("single_source")
        _rename["single_source"] = "single-source"
    if "repeat_offender_share" in view.columns:
        _top20_cols.append("repeat_offender_share")
        _rename["repeat_offender_share"] = "repeat-offenders"
    top = (view.sort_values("cis", ascending=False)
                .head(20)[_top20_cols]
                .rename(columns=_rename))
    with st.container(key="pv-table-overview"):
        st.dataframe(top, hide_index=True, width="stretch")
