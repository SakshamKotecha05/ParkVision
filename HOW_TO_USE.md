# How to Navigate ParkVision — A Plain-English User Guide

This is a step-by-step guide to actually using the website — what's on screen, what every button/slider/filter does, and which tab to open depending on what you're trying to find out. No background knowledge required; if you want the *why* behind the project, see `PROJECT_OVERVIEW.md` instead. This file is purely about *using the tool*.

---

## 0. Opening the site

1. Open the Demo Link (or run it locally: `streamlit run app.py`, then open the URL it prints — usually `http://localhost:8501`).
2. You'll land on a page titled **ParkVision**, with one line underneath it describing what it does, and **5 tabs** across the top:

   `Priority Zones` · `Forecast` · `Deployment Planner` · `Blind Spots` · `AI Briefings`

3. The page **opens on "Priority Zones"** by default — that's intentional, it's the right starting point for almost everyone. Click any tab name to switch; nothing reloads the page, no waiting.

**The whole site has no log-in, no settings page, and no "save" button to worry about.** Every number on screen is already computed — you're only ever filtering/viewing, never breaking anything. Click around freely.

---

## 1. Tab 1 — Priority Zones (start here)

**What you'll see, top to bottom:**

1. A big highlighted band: **"9.2% of 298,450 logged violations actually choke traffic flow."** This is the headline fact the whole tool is built around — read it first.
2. Three small stat cards: **Scored zones** (≈5,753), **Top zone CIS** (≈88.5), and **Junction-overlap proof** (≈85.0%, with a small **"Verified"** tag — that tag means this specific number was independently double-checked against real BTP junction data, not just produced by the model).
3. A **Filters** row with three controls:
   - **Police station** (dropdown, multi-select) — pick one or more stations to narrow everything below to just those.
   - **Minimum CIS** (slider) — drag right to hide low-priority zones and see only the worst offenders.
   - **Rising only** (checkbox) — tick this to see only zones the Forecast tab predicts are getting *worse*, not just the ones that are already bad.
4. A **map** — every dot is a zone. Bigger and redder = higher priority. Hover over any dot to see its zone ID, CIS score, station, and high-impact count.
5. A **Top 20 priority zones** table below the map — the same information as the map, in sortable list form, useful for screenshots or quick scanning without needing to hover.

**How to use it:**
- *"What are the worst spots in the whole city?"* → Just look at the map and table as-is, no filters needed.
- *"What are the worst spots in my station's area?"* → Pick your station from the **Police station** dropdown.
- *"Show me only the genuinely serious ones."* → Drag the **Minimum CIS** slider up until the list is a manageable size.
- *"What's about to get worse, not just what's already bad?"* → Tick **Rising only**.
- If you filter down to nothing, the page will just say *"No zones match the current filters"* — that's not a bug, just loosen a filter.

---

## 2. Tab 2 — Forecast

**What you'll see:**

1. A highlighted band showing the **backtest Spearman score** (≈0.849) with a **Verified** tag — this number means "we tested the forecast against real violations that happened later, and checked it got the ranking right."
2. Four stat cards: **Backtest Spearman**, **MAE** (average error size), **Zones validated**, and the **Validation window** (the date range used to test it).
3. A plain-language **info box** explaining honestly what the forecast can and can't tell you — read this, it's there so you don't over-trust the number.
4. A table of every zone, sorted by **risk score** (highest first), with a **trend** column — zones marked **🔺 rising** are predicted to keep getting worse.

**How to use it:**
- *"Which zones should I worry about tomorrow, not just today?"* → Scroll the table, look for 🔺 rising near the top.
- *"Is this forecast actually any good, or just guessing?"* → Read the info box and the Spearman number — it's stated honestly, including what it doesn't measure.
- There's no filter on this tab — it's meant to be scanned as one ranked list, not narrowed down. If you want a specific station's rising zones, use the **Rising only** checkbox back on Tab 1 instead.

---

## 3. Tab 3 — Deployment Planner

**What you'll see:**

1. A highlighted band: **"K=25 recommended patrol size"** — this is the tool's answer to "how many patrol units should I deploy?"
2. A **Patrol size K** slider — drag it left/right to test different patrol sizes (5, 10, 15, 20, 25, 30, 40, 50).
3. As you move the slider, four numbers update live: **High-impact covered** (%), **Random-patrol baseline** (%), **Efficiency vs random** (×), **Marginal gain** (%).
4. If you land exactly on K=25, a green success message confirms it's the recommended sweet spot.
5. A **chart** below: your coverage line (solid) vs. a random-placement baseline (dashed), with a marker at K=25.
6. A **reference patrol plan table** at the bottom — a fixed, ready-to-use list of the actual top-20 zones to send patrols to today.

**How to use it:**
- *"How many patrol units do I actually need?"* → Leave the slider at the default (K=25) — it's already the recommended answer.
- *"What if I only have 10 officers today?"* → Drag the slider to 10 and read the four numbers — you'll instantly see the coverage trade-off of having fewer units.
- *"Where do I literally send my patrol right now?"* → Scroll to the **reference patrol plan** table — it's a ranked, ready list (fixed at 20 zones, doesn't change with the slider).
- The slider only changes the *numbers and chart* — the reference table at the bottom always shows the same precomputed 20-zone plan, by design (it's the one the optimizer actually ran in full, not a live re-calculation).

---

## 4. Tab 4 — Blind Spots

**What you'll see:**

1. A highlighted band: **"58.6% of all enforcement effort sits with the top-10 busiest stations."** — this sets up the problem: some areas get watched a lot, others barely at all.
2. Two stat cards: **Blind-spot zones** (how many such zones exist) and **High-impact in blind spots** (how many serious violations are sitting in them).
3. A **map** — every dot here is a zone that's high-priority *but* currently under-patrolled. (No color-coding needed here — every dot on this map is, by definition, a problem.)
4. A table of all blind-spot zones, ranked.

**How to use it:**
- *"Where are we missing coverage entirely, not just under-prioritizing?"* → This whole tab answers that question. No filters needed — every zone shown here already qualifies as a blind spot.
- This is the simplest tab in the tool on purpose — it's meant to be read as a short, direct "go check these" list.

---

## 5. Tab 5 — AI Briefings

**What you'll see:**

1. A **Police station** dropdown — pick any of the 54 stations.
2. A **"Generate / Regenerate briefing"** button.
3. Below that, a written briefing in plain English — a short memo summarizing that station's top chokepoints, rising zones, today's patrol-plan zones, and any blind spots, in a few short paragraphs.

**How to use it:**
- *"I just want a quick written summary for my station, not a dashboard."* → Pick your station, read the briefing. That's it — no other steps.
- The briefing already exists for every station (pre-generated), so it normally appears instantly.
- Click **Generate / Regenerate briefing** if you want to refresh it after the underlying data changes, or just to see it regenerate live — you'll get a small confirmation message when it's done.
- This is the tab to show someone who doesn't want to learn the rest of the dashboard — it's a single readable paragraph instead of a map or table.

---

## 6. "I want to find X" — quick lookup table

| What you're trying to find | Go to | Do this |
|---|---|---|
| The single most important fact about this project | Tab 1 | Just read the headline band |
| Worst zones in my area | Tab 1 | Filter by **Police station** |
| Zones getting worse, not just already-bad | Tab 1 or Tab 2 | Tick **Rising only** (Tab 1) or scan 🔺 rows (Tab 2) |
| How many patrols I need | Tab 3 | Read the K=25 headline, or slide K to test other sizes |
| Exactly where to send today's patrol | Tab 3 | Scroll to the reference plan table |
| Areas nobody is watching | Tab 4 | Just open the tab — every row is one |
| A one-paragraph summary for my station | Tab 5 | Pick your station from the dropdown |
| Proof the tool isn't just guessing | Tab 1 (Junction-overlap, 85%) and Tab 2 (Spearman, 0.849) | Look for the **Verified** tag — that's the independently-checked number |

---

## 7. A 60-second tour (if you only have a minute)

1. Tab 1 → read the 9.2% headline and the **Verified** 85% tag. (15 sec)
2. Tab 3 → look at K=25 and slide it once to see the numbers move. (15 sec)
3. Tab 4 → glance at the 58.6% headline and the map. (10 sec)
4. Tab 5 → pick any station, read the briefing paragraph. (20 sec)

That covers the insight, the action, the gap, and the output — the whole story in four clicks.

---

## 8. Troubleshooting

- **A tab looks empty / says "No zones match the current filters."** You've filtered too narrowly on Tab 1 — loosen the **Minimum CIS** slider or clear the station selection.
- **The map doesn't load / looks blank.** Give it a second — pydeck maps render after the page's other elements. No internet-based map tiles are required, so this isn't a connectivity issue.
- **Numbers look slightly different from a screenshot in the deck.** The underlying data artifacts are versioned and may have been refreshed since a given screenshot was taken — the live numbers on screen are always the current ones.
- **The AI Briefings tab is slow the first time for a station.** It only happens once per station; after that the briefing is cached and loads instantly.

---

*This file lives at `Round2_gsd/HOW_TO_USE.md` — pure usage instructions, no project background. Pair it with `PROJECT_OVERVIEW.md` for the "why," or the README for installation/deploy steps.*
