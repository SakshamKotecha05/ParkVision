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
theme.render_hero()

data = load_all()

# Single-page scroll: the hero's top nav is the only nav. Each section gets
# an anchor the nav links + scroll cue jump to (the old below-hero tab bar
# is gone).
theme.section("zones")
tab_overview.render(data)

theme.section("forecast", divider=True)
tab_forecast.render(data)

theme.section("deploy", divider=True)
tab_deploy.render(data)

theme.section("blindspots", divider=True)
tab_blindspots.render(data)

theme.section("briefings", divider=True)
try:
    from parkvision.dashboard import tab_briefing
    tab_briefing.render(data)
except ImportError:
    st.info("AI Briefings tab arrives in Task 3.")
