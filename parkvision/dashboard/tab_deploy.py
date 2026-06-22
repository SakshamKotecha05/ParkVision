"""Tab 3 — Deployment Planner: K selector, ROI metrics, ROI curve, K=20 plan."""
from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from parkvision.dashboard import theme

RECOMMENDED_K = 25  # from deploy.recommend_k
PRECOMPUTED_PLAN_K = 20  # deploy_plan.parquet is fixed at K=20


def render(data: dict) -> None:
    roi: pd.DataFrame = data["roi_curve"]
    plan: pd.DataFrame = data["deploy_plan"]

    st.subheader("Deployment Planner")
    rec_row = roi.loc[roi["k"] == RECOMMENDED_K]
    rec_pct = float(rec_row["covered_pct"].iloc[0]) if not rec_row.empty else 0.0
    st.markdown(
        f"""
        <div class="pv-headline">
          <span class="big">K={RECOMMENDED_K}</span>
          <span class="sub">recommended patrol size — covers
          {rec_pct:.1f}% of high-impact violations at the best
          coverage-per-unit-effort knee on the ROI curve.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "Greedy max-coverage patrol plan. Pick a patrol size K to see the "
        "return-on-effort; the ranked zone list below is the precomputed "
        f"K={PRECOMPUTED_PLAN_K} reference plan (re-running the optimizer live "
        "is out of scope — no re-modelling in the demo).")

    k_values = sorted(roi["k"].tolist())
    default_idx = k_values.index(RECOMMENDED_K) if RECOMMENDED_K in k_values \
        else 0
    k = st.select_slider("Patrol size K", options=k_values,
                         value=k_values[default_idx])

    row = roi.loc[roi["k"] == k].iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("High-impact covered", f"{row['covered_pct']:.1f}%")
    c2.metric("Random-patrol baseline", f"{row['baseline_pct']:.1f}%")
    c3.metric("Efficiency vs random", f"{row['efficiency']:.1f}×")
    c4.metric("Marginal gain", f"{row['marginal_gain']:.1f}%")
    if k == RECOMMENDED_K:
        st.success(f"K={RECOMMENDED_K} is the recommended patrol size — "
                   "best coverage-per-unit-effort knee on the ROI curve.")

    st.markdown('<hr class="pv-rule">', unsafe_allow_html=True)
    st.markdown("##### ROI curve — coverage vs patrol size")
    curve = roi[["k", "covered_pct", "baseline_pct"]].copy()

    mono_axis = alt.Axis(labelFont=theme._FONT_MONO.split(",")[0].strip("'"),
                          titleFont=theme._FONT_MONO.split(",")[0].strip("'"))

    line_pv = alt.Chart(curve).mark_line(
        color=theme.BRAND, strokeWidth=2.5,
    ).encode(
        x=alt.X("k:Q", title="Patrol size K", axis=mono_axis),
        y=alt.Y("covered_pct:Q", title="Coverage %", axis=mono_axis),
        tooltip=["k", "covered_pct"],
    )
    line_baseline = alt.Chart(curve).mark_line(
        color=theme.INK_3, strokeWidth=2, strokeDash=[4, 4],
    ).encode(
        x="k:Q",
        y="baseline_pct:Q",
        tooltip=["k", "baseline_pct"],
    )
    rec_point_df = curve[curve["k"] == RECOMMENDED_K]
    rule_k = alt.Chart(rec_point_df).mark_rule(
        color=theme.INK_3, strokeDash=[2, 2], opacity=0.6,
    ).encode(x="k:Q")
    point_k = alt.Chart(rec_point_df).mark_point(
        color=theme.BRAND, size=90, filled=True,
    ).encode(x="k:Q", y="covered_pct:Q", tooltip=["k", "covered_pct"])

    chart = (line_pv + line_baseline + rule_k + point_k).properties(
        height=320,
        background=theme.PAPER,
    ).configure_view(
        strokeWidth=0,
    ).configure_axis(
        labelColor=theme.INK_3,
        titleColor=theme.INK_3,
        gridColor=theme.PAPER_3,
        domainColor=theme.PAPER_3,
    )
    st.altair_chart(chart, use_container_width=True)
    st.caption(f"Recommended operating point: K={RECOMMENDED_K} "
               f"({roi.loc[roi['k'] == RECOMMENDED_K, 'covered_pct'].iloc[0]:.1f}% "
               "high-impact covered).")

    st.markdown(f"##### Reference patrol plan (K={PRECOMPUTED_PLAN_K})")
    show = plan[["rank", "zone_id", "cis", "high_impact_covered",
                 "n_zones_covered"]].rename(
        columns={"cis": "CIS", "high_impact_covered": "high-impact covered",
                 "n_zones_covered": "zones covered"})
    with st.container(key="pv-table-deploy"):
        st.dataframe(show, hide_index=True, use_container_width=True)
