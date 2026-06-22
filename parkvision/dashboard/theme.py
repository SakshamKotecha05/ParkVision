"""Shared visual constants and helpers for the ParkVision dashboard.

Design language: warm SaaS-editorial — cream paper, bold restrained
display headlines, one coral brand accent used sparingly, soft-shadowed
white cards. A separate 5-stop severity scale (ochre -> oxblood) encodes
CIS / risk / blind-spot data so "high-priority" never reads as "this is a
brand-colored button." A "Verified" proof seal marks the two numbers in
the app that are independently validated against ground truth, visually
distinguishing them from plain model-output stats.
"""
from __future__ import annotations

import streamlit as st

# --- Locked brand tokens (do not alter) --------------------------------
PAPER = "#faf7f2"
PAPER_2 = "#f3ede0"
PAPER_3 = "#ede4d2"
CARD = "#fff"
INK = "#1a1714"
INK_2 = "#2b2723"
INK_3 = "#4a443d"
BRAND = "#d97757"
BRAND_INK = "#9f4b32"
BRAND_SOFT = "#fbe9df"
BRAND_LINE = "#f6cdb9"
R_MD = "8px"
R_LG = "12px"
R_XL = "16px"
SHADOW = "0 1px 0 #1a17140d, 0 4px 16px #1a17140f"
SHADOW_LG = "0 2px 0 #1a17140f, 0 24px 64px #1a171424"

# --- NEW severity / data-encoding scale (distinct from brand) ----------
# 5-stop ramp for CIS, map dots, rising/alarm flags, blind-spot highlight.
# Deliberately NOT the brand coral — "high-priority" should never read as
# "this is a brand button/link."
SEV_0 = "#e8c87a"  # low      ochre
SEV_1 = "#dd9f56"  # moderate amber-clay
SEV_2 = "#cf7340"  # elevated burnt
SEV_3 = "#b14d35"  # high     clay-red
SEV_4 = "#8a2f2e"  # critical oxblood
SEV_FLAG = SEV_3   # "rising ▲" / blind-spot text+marker color

_SEV_STOPS_RGB = [
    (232, 200, 122),  # sev-0
    (221, 159, 86),   # sev-1
    (207, 115, 64),   # sev-2
    (177, 77, 53),    # sev-3
    (138, 47, 46),    # sev-4
]

# WARN_RGBA: uniform blind-spot map color — now --sev-3 opaque.
WARN_RGBA = [177, 77, 53, 200]

_FONT_DISPLAY = "'Bricolage Grotesque', sans-serif"
_FONT_SANS = "'Schibsted Grotesk', -apple-system, 'Segoe UI', sans-serif"
_FONT_MONO = (
    "'JetBrains Mono', 'SFMono-Regular', 'Consolas', 'Menlo', monospace"
)

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700&family=Schibsted+Grotesk:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

.stApp {{ background-color: {PAPER}; }}
.block-container {{ padding-top: 2rem; max-width: 1180px; }}

h1, [data-testid="stHeading"] h1 {{
  font-family: {_FONT_DISPLAY};
  font-size: 40px;
  line-height: 1.05;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: {INK};
}}
h2, [data-testid="stHeading"] h2 {{
  font-family: {_FONT_DISPLAY};
  font-size: 26px;
  line-height: 1.15;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: {INK};
}}
h3, [data-testid="stHeading"] h3 {{
  font-family: {_FONT_SANS};
  font-size: 17px;
  line-height: 1.3;
  font-weight: 600;
  color: {INK};
}}

[data-testid="stCaptionContainer"], .stMarkdown p, .stMarkdown li {{
  font-family: {_FONT_SANS};
  color: {INK_3};
  font-size: 15px;
  line-height: 1.55;
}}

/* Eyebrow / section labels — "##### x" markdown headers render as h5 */
.stMarkdown h5 {{
  font-family: {_FONT_SANS};
  font-size: 11px;
  line-height: 1.2;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: {INK_3};
  margin-top: 0.4rem;
}}

/* --- Tabs: plain nav links, coral underline on active ---------------- */
[data-baseweb="tab-list"] {{
  background: transparent;
  border-bottom: 1px solid {PAPER_3};
  gap: 1.5rem;
}}
[data-baseweb="tab"] {{
  font-family: {_FONT_SANS};
  font-size: 14px;
  font-weight: 500;
  color: {INK_3};
  background: transparent;
  border: none;
  padding: 0.6rem 0.1rem;
}}
[data-baseweb="tab"]:hover {{
  color: {INK};
  background: transparent;
}}
[data-baseweb="tab"][aria-selected="true"] {{
  color: {INK};
  border-bottom: 2px solid {BRAND};
}}
[data-baseweb="tab-highlight"] {{
  background-color: transparent !important;
  box-shadow: none !important;
}}
[data-baseweb="tab-border"] {{
  background-color: transparent !important;
}}

/* --- Metrics: white shadow cards -------------------------------------- */
[data-testid="stMetric"] {{
  background: {CARD};
  border-radius: {R_LG};
  box-shadow: {SHADOW};
  padding: 1rem;
}}
[data-testid="stMetricValue"] {{
  font-family: {_FONT_MONO};
  font-variant-numeric: tabular-nums;
  font-size: 28px;
  font-weight: 500;
  color: {INK};
}}
[data-testid="stMetricLabel"] {{
  font-family: {_FONT_SANS};
  color: {INK_3};
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 11px;
  font-weight: 600;
}}

/* --- Headline band — the dashboard's signature element ---------------- */
.pv-headline {{
  position: relative;
  display: flex;
  align-items: baseline;
  gap: 0.9rem;
  background: {CARD};
  box-shadow: {SHADOW_LG};
  border-radius: {R_XL};
  border-left: 3px solid {BRAND};
  padding: 1.2rem 1.4rem;
  margin-bottom: 1.1rem;
}}
.pv-headline .big {{
  font-family: {_FONT_DISPLAY};
  font-size: 34px;
  font-weight: 700;
  color: {INK};
  font-variant-numeric: tabular-nums;
  line-height: 1;
  white-space: nowrap;
}}
.pv-headline .sub {{
  font-family: {_FONT_SANS};
  color: {INK_3};
  font-size: 15px;
  line-height: 1.55;
}}

/* Proof variant — dashed top border + seal pinned top-right, used to
   wrap a headline stat that is independently verified, not model output. */
.pv-headline.pv-verified-card {{
  border-top: 2px dashed {BRAND_LINE};
}}
.pv-headline.pv-verified-card .pv-verified {{
  position: absolute;
  top: -0.7rem;
  right: 1.1rem;
}}

/* --- Verified proof seal (inline + card variants) ---------------------- */
.pv-verified {{
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-family: {_FONT_SANS};
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: {BRAND_INK};
  background: {BRAND_SOFT};
  border: 1px solid {BRAND_LINE};
  border-radius: {R_MD};
  padding: 0.2rem 0.55rem;
  white-space: nowrap;
}}
.pv-verified::before {{
  content: "";
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 1.5px solid {BRAND_INK};
  background:
    linear-gradient(135deg, transparent 42%, {BRAND_INK} 42%, {BRAND_INK} 52%, transparent 52%),
    linear-gradient(45deg, transparent 55%, {BRAND_INK} 55%, {BRAND_INK} 65%, transparent 65%);
}}

/* Thin hairline used instead of Streamlit's default divider */
.pv-rule {{
  border: none;
  border-top: 1px solid {PAPER_3};
  margin: 1.1rem 0 0.9rem 0;
}}

.pv-tag {{
  display: inline-block;
  font-family: {_FONT_MONO};
  font-size: 0.72rem;
  letter-spacing: 0.03em;
  color: {INK_3};
  border: 1px solid {PAPER_3};
  border-radius: 999px;
  padding: 0.1rem 0.55rem;
  margin-right: 0.3rem;
}}

/* --- Buttons: black pill CTA -------------------------------------------- */
.stButton button, button[kind="secondary"], button[kind="primary"] {{
  background: {INK};
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 8px 18px;
  font-family: {_FONT_SANS};
  font-weight: 500;
}}
.stButton button:hover, button[kind="secondary"]:hover, button[kind="primary"]:hover {{
  background: {INK_2};
  color: #fff;
}}

/* --- Multiselect / selectbox -------------------------------------------- */
[data-baseweb="select"] > div {{
  background: {CARD};
  border: 1px solid {PAPER_3};
  border-radius: {R_MD};
}}
[data-baseweb="tag"] {{
  background: {BRAND_SOFT} !important;
  color: {BRAND_INK} !important;
  border-radius: {R_MD};
}}
[data-baseweb="popover"] [data-baseweb="menu"] {{
  background: {CARD};
}}

/* --- Slider / select_slider --------------------------------------------- */
[data-baseweb="slider"] [data-testid="stTickBar"] {{
  background: {PAPER_3};
}}
div[data-baseweb="slider"] > div > div > div {{
  background: {PAPER_3};
}}
div[data-baseweb="slider"] > div > div > div > div {{
  background: {BRAND};
}}
[data-baseweb="slider"] div[role="slider"] {{
  background: {BRAND};
  border-color: {BRAND};
}}
[data-testid="stTickBarMin"], [data-testid="stTickBarMax"],
[data-baseweb="slider"] [data-testid="stThumbValue"] {{
  font-family: {_FONT_MONO};
  color: {INK_3};
}}

/* --- Checkbox ------------------------------------------------------------- */
[data-baseweb="checkbox"] span:first-child {{
  background: {CARD};
  border-color: {PAPER_3};
}}
[data-baseweb="checkbox"] input:checked + span {{
  background: {BRAND} !important;
  border-color: {BRAND} !important;
}}

/* --- Alerts (st.info / st.success) --------------------------------------- */
[data-testid="stAlert"] {{
  background: {CARD};
  border-radius: {R_LG};
  box-shadow: {SHADOW};
  border-left: 3px solid {INK_3};
  padding: 0.9rem 1.1rem;
}}
[data-testid="stAlert"] p {{
  color: {INK_2};
}}
[data-testid="stAlertContentSuccess"] {{
  border-left-color: {BRAND};
}}
div[data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) {{
  border-left: 3px solid {INK_3};
}}
div[data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]) {{
  border-left: 3px solid {BRAND};
}}

/* --- DataFrame container shell --------------------------------------------
   Applied via st.container(key="pv-table-..."), which Streamlit renders as
   a real wrapping DOM element with CSS class "st-key-pv-table-...". A pair
   of bare st.markdown('<div>')/st.markdown('</div>') calls would NOT nest —
   each st.* call creates its own sibling block — so a real container with a
   stable key is required for this to visually wrap the widget. */
[class*="st-key-pv-table"] {{
  background: {CARD};
  border-radius: {R_LG};
  box-shadow: {SHADOW};
  border: 1px solid {PAPER_3};
  padding: 8px;
}}
[class*="st-key-pv-table"] [data-testid="stDataFrame"] {{
  font-family: {_FONT_MONO};
}}
[class*="st-key-pv-table"] [data-testid="stElementToolbar"] {{
  background: {PAPER};
}}

/* --- Briefing markdown card --------------------------------------------
   Applied via st.container(key="pv-doc") -> class "st-key-pv-doc". */
[class*="st-key-pv-doc"] {{
  background: {CARD};
  border-radius: {R_LG};
  box-shadow: {SHADOW};
  padding: 1.6rem 1.8rem;
}}
[class*="st-key-pv-doc"] h1 {{
  font-family: {_FONT_DISPLAY};
  font-size: 26px;
  font-weight: 600;
  color: {INK};
}}
[class*="st-key-pv-doc"] h2 {{
  font-family: {_FONT_SANS};
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: {INK_3};
  margin-top: 1.4rem;
}}
[class*="st-key-pv-doc"] p, [class*="st-key-pv-doc"] li {{
  font-family: {_FONT_SANS};
  font-size: 15px;
  line-height: 1.55;
  color: {INK_2};
}}
[class*="st-key-pv-doc"] strong {{
  color: {INK};
}}
[class*="st-key-pv-doc"] hr {{
  border: none;
  border-top: 1px solid {PAPER_3};
  margin: 1.1rem 0;
}}

/* Rising-flag glyph/text — severity flag color, not brand coral */
.pv-flag {{
  color: {SEV_FLAG};
  font-weight: 500;
}}
</style>
"""


def inject_css() -> None:
    """Inject the dashboard's custom CSS once per page."""
    st.markdown(_CSS, unsafe_allow_html=True)


def cis_to_color(cis: float, cis_max: float) -> list[int]:
    """Map a CIS value to an [r, g, b, a] severity-scale gradient for pydeck.

    Interpolates across the 5 severity stops (--sev-0 ochre .. --sev-4
    oxblood) instead of the old amber->red ramp, so map dots use the
    data-encoding scale rather than the brand color.
    """
    if cis_max <= 0:
        frac = 0.0
    else:
        frac = max(0.0, min(1.0, cis / cis_max))

    n_stops = len(_SEV_STOPS_RGB)
    # Position along the 0..n_stops-1 stop index.
    pos = frac * (n_stops - 1)
    lo = int(pos)
    hi = min(lo + 1, n_stops - 1)
    t = pos - lo

    r0, g0, b0 = _SEV_STOPS_RGB[lo]
    r1, g1, b1 = _SEV_STOPS_RGB[hi]
    r = int(r0 + (r1 - r0) * t)
    g = int(g0 + (g1 - g0) * t)
    b = int(b0 + (b1 - b0) * t)
    a = int(110 + 125 * frac)
    return [r, g, b, a]
