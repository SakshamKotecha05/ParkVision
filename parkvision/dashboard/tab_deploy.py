"""Tab 3 — Deployment Planner: K selector, ROI metrics, ROI curve, K=20 plan."""
from __future__ import annotations

import pandas as pd
import streamlit as st

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
    curve = roi.set_index("k")[["covered_pct", "baseline_pct"]].rename(
        columns={"covered_pct": "ParkVision coverage %",
                 "baseline_pct": "Random baseline %"})
    st.line_chart(curve)
    st.caption(f"Recommended operating point: K={RECOMMENDED_K} "
               f"({roi.loc[roi['k'] == RECOMMENDED_K, 'covered_pct'].iloc[0]:.1f}% "
               "high-impact covered).")

    st.markdown(f"##### Reference patrol plan (K={PRECOMPUTED_PLAN_K})")
    show = plan[["rank", "zone_id", "cis", "high_impact_covered",
                 "n_zones_covered"]].rename(
        columns={"cis": "CIS", "high_impact_covered": "high-impact covered",
                 "n_zones_covered": "zones covered"})
    st.dataframe(show, hide_index=True, use_container_width=True)
