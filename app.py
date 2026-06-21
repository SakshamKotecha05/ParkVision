"""ParkVision — jury-facing Streamlit dashboard.

Run:  streamlit run app.py
Reads the 8 pre-built artifacts via parkvision.app_data (read-only).
"""
from __future__ import annotations

import streamlit as st

from parkvision.app_data import load_all
from parkvision.dashboard import (
    tab_blindspots,
    tab_deploy,
    tab_forecast,
    tab_overview,
    theme,
)

st.set_page_config(page_title="ParkVision — Bengaluru Enforcement",
                   page_icon="🚦", layout="wide")
theme.inject_css()

st.title("ParkVision")
st.caption("Congestion-Impact ranking for Bengaluru parking-violation "
           "enforcement — find the few zones that choke traffic flow.")

data = load_all()

tab_labels = ["Priority Zones", "Forecast", "Deployment Planner",
              "Blind Spots", "AI Briefings"]
t1, t2, t3, t4, t5 = st.tabs(tab_labels)

with t1:
    tab_overview.render(data)
with t2:
    tab_forecast.render(data)
with t3:
    tab_deploy.render(data)
with t4:
    tab_blindspots.render(data)
with t5:
    try:
        from parkvision.dashboard import tab_briefing
        tab_briefing.render(data)
    except ImportError:
        st.info("AI Briefings tab arrives in Task 3.")
