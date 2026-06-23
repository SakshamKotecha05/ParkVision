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

.stApp {{ background-color: {PAPER}; overflow-x: hidden; }}
html {{ scroll-behavior: smooth; }}
/* Hide Streamlit's top chrome so the full-screen hero owns the very top. */
header[data-testid="stHeader"] {{ display: none; }}
/* padding-top 0 so the hero sits flush at the top. */
.block-container {{ padding-top: 0; max-width: 1180px; }}
/* The inject_css() call renders a markdown block that holds only this
   <style>; its flex gap pushed the hero ~16px down. Collapse that one
   block (the style still applies — style tags are global) so the hero is
   flush at the top. Scoped to a markdown-with-style so it never hits a
   chart/map container. */
[data-testid="stElementContainer"]:has([data-testid="stMarkdownContainer"] > style) {{
  display: none;
}}
/* Anchor targets for the hero nav's single-page scroll. */
.pv-section {{ display: block; height: 0; scroll-margin-top: 1rem; }}

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

/* --- Hero: full-viewport cinematic video landing ----------------------
   Full-bleed 100vw x 100svh window into Bengaluru's streets. A top nav
   sits over the footage; scrolling past the hero reveals the live
   dashboard below. The "Verified" seal is lifted onto the footage — the
   one thing that separates ParkVision from a pretty model demo. */
.pv-hero {{
  position: relative;
  /* break out of the centered, max-width block-container to full bleed */
  width: 100vw;
  margin-left: calc(50% - 50vw);
  margin-right: calc(50% - 50vw);
  margin-bottom: 2.2rem;
  min-height: 100svh;
  overflow: hidden;
  /* warm fallback while the video buffers / under reduced-motion */
  background: linear-gradient(135deg, {INK_2} 0%, {INK} 70%);
  isolation: isolate;
}}
.pv-hero video {{
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
}}
/* Warm ink scrim — keeps copy legible over ANY video frame (the footage
   runs through bright daytime). Tinted to {INK}, never flat black. */
.pv-hero::after {{
  content: "";
  position: absolute;
  inset: 0;
  z-index: 1;
  background:
    linear-gradient(102deg, rgba(26,23,20,0.9) 0%, rgba(26,23,20,0.66) 34%,
                    rgba(26,23,20,0.18) 64%, rgba(26,23,20,0) 88%),
    linear-gradient(0deg, rgba(26,23,20,0.82) 0%, rgba(26,23,20,0.36) 30%,
                    rgba(26,23,20,0) 58%),
    /* uniform contrast floor so white copy reads over any bright frame */
    linear-gradient(rgba(26,23,20,0.26), rgba(26,23,20,0.26));
}}

/* --- Top nav (over the hero) --------------------------------------- */
.pv-nav {{
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: clamp(1.1rem, 2.4vw, 1.7rem) clamp(1.4rem, 4vw, 3.2rem);
}}
.pv-nav__brand {{
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: {_FONT_DISPLAY};
  font-weight: 700;
  font-size: 20px;
  letter-spacing: -0.01em;
  color: #fff;
  text-shadow: 0 1px 12px rgba(0,0,0,0.5);
}}
.pv-nav__brand::before {{
  content: "";
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: {BRAND};
  box-shadow: 0 0 0 4px rgba(217,119,87,0.28);
}}
.pv-nav__links {{
  display: flex;
  align-items: center;
  gap: clamp(0.9rem, 2vw, 1.9rem);
}}
/* .pv-hero prefix out-specifies Streamlit's own `.stMarkdown a` link color,
   which would otherwise paint these links blue. */
.pv-hero .pv-nav__links a {{
  font-family: {_FONT_SANS};
  font-size: 13.5px;
  font-weight: 500;
  letter-spacing: 0.01em;
  color: rgba(255,255,255,0.86);
  text-decoration: none;
  text-shadow: 0 1px 8px rgba(0,0,0,0.5);
  transition: color 0.15s ease;
}}
.pv-hero .pv-nav__links a:hover {{ color: #fff; }}
.pv-hero .pv-nav__links a:focus-visible {{ outline: 2px solid #f0a890; outline-offset: 4px; }}

/* --- Centered hero content ----------------------------------------- */
.pv-hero__inner {{
  position: relative;
  z-index: 2;
  min-height: 100svh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.55rem;
  max-width: 780px;
  padding: clamp(2rem, 6vh, 5rem) clamp(1.4rem, 4vw, 3.2rem);
}}
/* Selectors are prefixed with .pv-hero to out-specify Streamlit's own
   heading / .stMarkdown p rules, which would otherwise force the copy to
   the dark ink body color over the video. */
.pv-hero .pv-hero__eyebrow {{
  font-family: {_FONT_SANS};
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: {BRAND_LINE};
  display: flex;
  align-items: center;
  gap: 0.6rem;
  text-shadow: 0 1px 8px rgba(0,0,0,0.5);
}}
.pv-hero .pv-hero__eyebrow::before {{
  content: "";
  width: 24px;
  height: 2px;
  background: {BRAND};
  display: inline-block;
}}
.pv-hero .pv-hero__title {{
  font-family: {_FONT_DISPLAY};
  font-weight: 700;
  font-size: clamp(38px, 6.6vw, 82px);
  line-height: 1.0;
  letter-spacing: -0.03em;
  color: #fff;
  margin: 0.1rem 0;
  text-wrap: balance;
  text-shadow: 0 1px 2px rgba(0,0,0,0.6), 0 2px 10px rgba(0,0,0,0.55),
               0 6px 28px rgba(0,0,0,0.4);
}}
.pv-hero .pv-hero__title .accent {{ color: #f0a890; }}
.pv-hero .pv-hero__sub {{
  font-family: {_FONT_SANS};
  font-size: clamp(14px, 1.6vw, 17px);
  line-height: 1.5;
  color: rgba(255,255,255,0.92);
  max-width: 50ch;
  margin: 0.15rem 0 0.25rem 0;
  text-shadow: 0 1px 10px rgba(0,0,0,0.55);
}}
.pv-hero__proof {{
  display: flex;
  align-items: center;
  gap: 0.7rem;
  flex-wrap: wrap;
  margin-top: 0.3rem;
}}
/* On-video variant of the signature seal */
.pv-hero__proof .pv-verified {{
  color: #fff;
  background: rgba(217,119,87,0.24);
  border: 1px solid rgba(246,205,185,0.55);
  -webkit-backdrop-filter: blur(6px);
  backdrop-filter: blur(6px);
}}
.pv-hero__proof .pv-verified::before {{
  border-color: #fff;
  background:
    linear-gradient(135deg, transparent 42%, #fff 42%, #fff 52%, transparent 52%),
    linear-gradient(45deg, transparent 55%, #fff 55%, #fff 65%, transparent 65%);
}}
.pv-hero__proofnote {{
  font-family: {_FONT_MONO};
  font-size: 12px;
  color: rgba(255,255,255,0.82);
  letter-spacing: 0.01em;
  text-shadow: 0 1px 8px rgba(0,0,0,0.5);
}}

/* --- Scroll cue: a pill that invites the reveal of the dashboard ----- */
.pv-hero .pv-hero__scroll {{
  position: absolute;
  left: clamp(1.4rem, 4vw, 3.2rem);
  bottom: clamp(1.3rem, 3.5vh, 2.4rem);
  z-index: 3;
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.4rem 0.4rem 0.4rem 1.1rem;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.28);
  background: rgba(26,23,20,0.34);
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
  font-family: {_FONT_SANS};
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.04em;
  color: #fff;
  text-decoration: none;
  text-shadow: 0 1px 8px rgba(0,0,0,0.4);
  transition: border-color 0.18s ease, background 0.18s ease,
              transform 0.18s ease;
}}
.pv-hero .pv-hero__scroll:hover {{
  border-color: rgba(246,205,185,0.7);
  background: rgba(217,119,87,0.32);
  transform: translateY(-1px);
}}
.pv-hero .pv-hero__scroll:focus-visible {{ outline: 2px solid #f0a890; outline-offset: 4px; }}
.pv-hero .pv-hero__scroll .chev {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #fff;
  color: {INK};
  font-size: 15px;
  font-weight: 700;
  text-shadow: none;
}}

@media (max-width: 640px) {{
  .pv-nav__links {{ display: none; }}
  .pv-hero__sub {{ display: none; }}
}}
@media (prefers-reduced-motion: reduce) {{
  html {{ scroll-behavior: auto; }}
  .pv-hero video {{ display: none; }}
}}
</style>
"""


def inject_css() -> None:
    """Inject the dashboard's custom CSS once per page."""
    st.markdown(_CSS, unsafe_allow_html=True)


# Served from ./static/ via [server] enableStaticServing in config.toml.
# Nav links + scroll cue point at #pv-dash, the anchor rendered just before
# the dashboard tabs in app.py.
_HERO_HTML = """
<section class="pv-hero">
  <video autoplay muted loop playsinline preload="auto" aria-hidden="true">
    <source src="app/static/hero_edit.mp4" type="video/mp4">
  </video>
  <nav class="pv-nav">
    <div class="pv-nav__brand">ParkVision</div>
    <div class="pv-nav__links">
      <a href="#zones">Priority Zones</a>
      <a href="#forecast">Forecast</a>
      <a href="#deploy">Deployment</a>
      <a href="#blindspots">Blind Spots</a>
      <a href="#briefings">AI Briefings</a>
    </div>
  </nav>
  <div class="pv-hero__inner">
    <div class="pv-hero__eyebrow">Bengaluru Traffic Police · Congestion Intelligence</div>
    <div class="pv-hero__title" role="heading" aria-level="1">The few blocks that <span class="accent">choke the city.</span></div>
    <p class="pv-hero__sub">ParkVision scores every parking-violation zone by how
       much it strangles traffic flow — so enforcement hits the 9% that actually
       jam Bengaluru, not the 91% that don't.</p>
    <div class="pv-hero__proof">
      <span class="pv-verified">Verified</span>
      <span class="pv-hero__proofnote">Ranking validated against real road junctions</span>
    </div>
  </div>
  <a class="pv-hero__scroll" href="#zones">Scroll to explore <span class="chev" aria-hidden="true">↓</span></a>
</section>
"""


def render_hero() -> None:
    """Render the full-viewport video hero landing at the top of the page."""
    st.markdown(_HERO_HTML, unsafe_allow_html=True)


def section(anchor: str, divider: bool = False) -> None:
    """Emit an anchor target (and optional hairline divider) for the hero
    nav's single-page scroll. Replaces the old below-hero tab bar."""
    html = ""
    if divider:
        html += '<hr class="pv-rule" style="margin:2.4rem 0 2rem;">'
    html += f'<div id="{anchor}" class="pv-section"></div>'
    st.markdown(html, unsafe_allow_html=True)


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
