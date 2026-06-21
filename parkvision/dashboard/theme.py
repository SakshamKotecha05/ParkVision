"""Shared visual constants and helpers for the ParkVision dashboard.

Design language: a traffic-control "ops console" — a cool near-black base,
monospace numerals for metrics and zone IDs (read like a console readout),
and a two-color severity gradient (amber -> red) reused across every map and
headline so the eye learns one rule: amber is attention, red is alarm.

Keeps the look intentional, not the Streamlit-default grey/sans look.
"""
from __future__ import annotations

import streamlit as st

# --- Token system -----------------------------------------------------
# Required public names (Task 3 / other tabs import these): INK, ACCENT,
# WARN, MUTED. PANEL/OK_GREEN are additional tokens used only inside this
# module's CSS, not part of the required interface.
INK = "#0B0D12"      # near-black console base (cooler than Streamlit default)
ACCENT = "#FFB020"   # amber — priority / CIS high / attention
WARN = "#FF4D4D"     # red — high-impact / blind spots / alarm
MUTED = "#7B8496"    # cool grey-blue secondary text

PANEL = "#131722"        # card surface, subtle lift off INK
PANEL_BORDER = "#262C3D"
OK_GREEN = "#3DDC97"      # sparing use — "recommended" / success states

# WARN as an opaque pydeck RGBA — used where every point should read as
# "alarm" (e.g. the Blind Spots map, which is uniformly high-severity).
WARN_RGBA = [255, 77, 77, 190]

_FONT_MONO = (
    "'IBM Plex Mono', 'SFMono-Regular', 'Consolas', 'Menlo', monospace"
)
_FONT_SANS = (
    "-apple-system, 'Inter', 'Segoe UI', sans-serif"
)

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');

.stApp {{ background-color: {INK}; }}
.block-container {{ padding-top: 2rem; max-width: 1200px; }}

h1, h2, h3 {{
  font-family: {_FONT_SANS};
  letter-spacing: -0.015em;
  color: #E8EAF0;
}}

[data-testid="stCaptionContainer"], .stMarkdown p, .stMarkdown li {{
  color: {MUTED};
}}

/* Console-style metrics: tabular monospace numerals */
[data-testid="stMetricValue"] {{
  font-family: {_FONT_MONO};
  font-variant-numeric: tabular-nums;
  color: #E8EAF0;
}}
[data-testid="stMetricLabel"] {{
  color: {MUTED};
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-size: 0.72rem;
}}
[data-testid="stMetric"] {{
  background: {PANEL};
  border: 1px solid {PANEL_BORDER};
  border-radius: 10px;
  padding: 0.85rem 1rem;
}}

/* Headline status-bar — the dashboard's signature element. Every tab opens
   with one: a single dark band, big amber monospace numeral, thin muted
   label, echoing a real ops-console readout rather than a generic banner. */
.pv-headline {{
  display: flex;
  align-items: baseline;
  gap: 0.9rem;
  background: {PANEL};
  border: 1px solid {PANEL_BORDER};
  border-left: 3px solid {ACCENT};
  border-radius: 8px;
  padding: 1rem 1.3rem;
  margin-bottom: 1.1rem;
}}
.pv-headline .big {{
  font-family: {_FONT_MONO};
  font-size: 2.3rem;
  font-weight: 700;
  color: {ACCENT};
  font-variant-numeric: tabular-nums;
  line-height: 1;
  white-space: nowrap;
}}
.pv-headline .sub {{
  color: {MUTED};
  font-size: 0.92rem;
  line-height: 1.35;
}}

/* Thin amber-tinted hairline used instead of Streamlit's default divider */
.pv-rule {{
  border: none;
  border-top: 1px solid {PANEL_BORDER};
  margin: 1.1rem 0 0.9rem 0;
}}

.pv-tag {{
  display: inline-block;
  font-family: {_FONT_MONO};
  font-size: 0.72rem;
  letter-spacing: 0.03em;
  color: {MUTED};
  border: 1px solid {PANEL_BORDER};
  border-radius: 999px;
  padding: 0.1rem 0.55rem;
  margin-right: 0.3rem;
}}

/* Dataframes / tables: zone IDs read as console output */
[data-testid="stDataFrame"] {{
  font-family: {_FONT_MONO};
}}
</style>
"""


def inject_css() -> None:
    """Inject the dashboard's custom CSS once per page."""
    st.markdown(_CSS, unsafe_allow_html=True)


def cis_to_color(cis: float, cis_max: float) -> list[int]:
    """Map a CIS value to an [r, g, b, a] amber->red gradient for pydeck."""
    if cis_max <= 0:
        frac = 0.0
    else:
        frac = max(0.0, min(1.0, cis / cis_max))
    # amber (255,176,32) at low end -> red (255,77,77) at high end
    r = int(255 + (255 - 255) * frac)
    g = int(176 + (77 - 176) * frac)
    b = int(32 + (77 - 32) * frac)
    a = int(90 + 120 * frac)
    return [r, g, b, a]
