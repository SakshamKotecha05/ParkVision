"""Tab 2 — Forecast & Rising Hotspots: ranked risk table + honest framing."""
from __future__ import annotations

import pandas as pd
import streamlit as st


def render(data: dict) -> None:
    forecast: pd.DataFrame = data["forecast"]
    metrics: dict = data["forecast_metrics"]

    st.subheader("Forecast & Rising Hotspots")
    st.markdown(
        f"""
        <div class="pv-headline pv-verified-card">
          <span class="pv-verified">Verified</span>
          <span class="big">{metrics.get('spearman', 0):.3f}</span>
          <span class="sub">backtest Spearman rank correlation between
          forecast risk and actual next-period violations on held-out data —
          the forecast ranks zones in the right order, not just the right
          ballpark.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Backtest Spearman", f"{metrics.get('spearman', 0):.3f}")
    m2.metric("MAE", f"{metrics.get('mae', 0):.2f}")
    m3.metric("Zones validated", f"{metrics.get('n_zones_valid', 0):,}")
    train_end = metrics.get("train_end", "?")
    valid_end = metrics.get("valid_end", "?")
    m4.metric("Validation window", f"→ {valid_end}",
              help=f"Trained through {train_end}; validated through {valid_end}.")

    framing = metrics.get("framing")
    if framing:
        st.info(framing)  # honesty/credibility requirement — do NOT drop

    st.markdown('<hr class="pv-rule">', unsafe_allow_html=True)
    st.markdown("##### Zones by forecast risk")
    df = forecast.sort_values("risk", ascending=False).copy()
    # NOTE: st.dataframe's glide-grid renders cell text as plain text, not
    # HTML, so the rising-flag color comes from column_config TextColumn's
    # help/width only for glyph; we keep the glyph plain and rely on the
    # caption + glyph itself (sev-flag color is documented in theme.py
    # .pv-flag for any future HTML-rendered usage of this label).
    df["trend"] = df["rising"].map(lambda r: "\U0001F53A rising" if bool(r) else "—")
    show = df[["zone_id", "risk", "slope", "trend"]].rename(
        columns={"zone_id": "zone", "risk": "risk score", "slope": "trend slope"})
    with st.container(key="pv-table-forecast"):
        st.dataframe(show, hide_index=True, width="stretch")
    st.caption(
        f"{int(df['rising'].sum())} zones flagged rising "
        f"(positive trend slope) out of {len(df):,} forecastable zones.")
