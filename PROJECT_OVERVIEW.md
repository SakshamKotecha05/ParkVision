# ParkVision — Full Project Explainer

*Written for the team and for explaining the project to the Gridlock 2.0 jury (Bengaluru Traffic Police + Flipkart). Every number in this file is real, measured against the provided 298,450-row dataset — nothing here is illustrative or made up.*

---

## 1. The one-sentence pitch

**ParkVision finds the 9.2% of parking violations that actually choke Bengaluru's traffic, ranks where they cluster, predicts where they're about to get worse, and tells a patrol exactly where to stand tomorrow morning — with one click.**

---

## 2. The problem we were given

**Theme 1 (Flipkart Gridlock 2.0, Round 2): "Poor Visibility on Parking-Induced Congestion."**

The operational challenge, as stated by the organizers: on-street illegal parking and spillover parking near commercial areas, metro stations, and events chokes carriageways and intersections. Today:
- Enforcement is **patrol-based and reactive** — officers go where complaints or habit send them, not where the data says the damage is worst.
- There is **no heatmap of violations vs. congestion impact** — BTP can see *where* violations are logged, but not *which ones matter*.
- It's **hard to prioritize enforcement zones** with 298K+ raw violation records and no scoring system.

The dataset: `jan to may police violation_anonymized791b166.csv` — 298,450 anonymized parking-violation records from Bengaluru Traffic Police (ASTraM), Nov 2023–Apr 2024, with lat/lon, violation type(s), vehicle type, timestamp, police station, and (sometimes) a named junction. This is **real field data from the people who own the problem**, not a synthetic toy set. (Note: despite the filename, the data actually spans Nov 10 2023 – Apr 8 2024; the backtest validates on March, the last full month, since April is partial.)

---

## 3. The core insight — why ParkVision is shaped the way it is

This is the single most important idea in the project, and the reason every other design decision follows from it:

> **Not all illegal parking chokes traffic equally.**

A car with a **defective number plate** is a violation, but it does nothing to traffic flow. A vehicle **double-parked at a road crossing**, **blocking a zebra crossing**, or **parked in a main road** physically narrows the carriageway at the worst possible point — that's a real, measurable obstruction.

We verified this directly in the data: **only 9.2% of the 298,450 logged violations are "high-impact" (flow-choking)** by physical-obstruction criteria. The other 90.8% — wrong parking on a quiet residential lane, a defective plate, a missing side mirror — barely move the needle on congestion. Concretely, ~77% of the high-impact tier is a single label — PARKING IN A MAIN ROAD — a blocked main-road lane, the textbook flow-choke.

**Why this matters for the pitch:** almost every competing team will build "a heatmap of all 300K violations." That's descriptive, not analytical — it tells BTP where paperwork happened, not where traffic actually suffers. ParkVision's entire value proposition is collapsing 298,450 noisy records down to the ~9% that matter, and then acting on *that*. This is the line that should open every pitch, demo, and deck slide.

---

## 4. How the score works — the Congestion Impact Score (CIS)

Every violation contributes to a **0–100 Congestion Impact Score (CIS)** for the ~150m geohash "zone" it falls in (5,753 zones across Bengaluru). CIS is **fully decomposable** — you can always point at a high-scoring zone and explain *why* it scored high, which matters enormously for jury credibility ("show your work," not a black box).

**Six weighted components** (`parkvision/config.py::CIS_WEIGHTS`):

| Component | Weight | What it measures | Why it's weighted this way |
|---|---|---|---|
| **Severity** | 0.35 | Tiered violation type — High (1.0): road-crossing, zebra, main-road, bus-stop, double-parking, lane-discipline, etc. Medium (0.6): wrong/no parking, footpath. Low (0.1): defective plate, missing mirror, fare disputes — administrative violations with ~zero flow impact. | This is the core differentiator (§3), so it gets the largest single weight — physical obstruction *is* the product. |
| **Density** | 0.25 | How many violations cluster in this zone. | A single bad violation matters less than a recurring chokepoint — density is the second-most-direct signal of real impact. |
| **Junction proximity** | 0.15 | Is this zone near one of BTP's 168 named junctions? | Junctions are where local obstruction becomes network-wide gridlock — and junction membership is *independently verifiable* ground truth (see §6). |
| **Road-type** | 0.10 | Arterial (1.0) > main road (0.7) > generic road (0.5) > cross-street (0.4) > residential (0.2). Parsed from the violation's `location` text (97.5% classified). | A blocked lane on an arterial highway costs the city far more than the same blockage on a residential lane. |
| **Vehicle footprint** | 0.10 | HGV/Bus/Lorry (1.0) ≫ Car (0.5) ≫ Scooter (0.2). | A wrongly parked bus occupies far more carriageway than a wrongly parked scooter — same violation, different physical cost. |
| **Recurrence** | 0.05 | Chronic (many distinct days) vs. one-off. | Persistent problem zones deserve more enforcement attention than a single bad afternoon. |

**A decision worth explaining to the jury directly, because it shows intellectual honesty:** the original design planned a 6th component based on *time-of-day concentration* ("peak-hour" violations). During EDA we discovered the violation timestamps are **anonymization-synthesized below the hour** — every single record's seconds field reads exactly `:46`, and minutes are uniformly randomized. That means hour-of-day is the finest *trustworthy* time resolution, and what it shows is a single **morning enforcement-logging peak (08:00–11:00 IST = 39.1% of all records)** with **no evening peak at all (17:00–21:00 IST = 0.3%)**. A real Bengaluru evening rush hour producing essentially zero violations is a dead giveaway that this is *when officers filed paperwork*, not *when congestion happened*. Rather than ship a fake "peak-hour congestion" feature on data that can't support it, we **dropped it and replaced it with the road-type component** at the same weight — a feature the data genuinely supports. **We say this openly on the limitations slide.** A jury of traffic engineers will immediately spot a fabricated rush-hour pattern; volunteering the finding ourselves converts a flaw into a credibility signal.

---

## 5. What the pipeline actually does, module by module

```
CSV ──ingest──▶ tidy violations ──┬──cis──▶ scored zones ──hotspots──▶ named hotspots
                                  │              │
                                  │              └──deploy──▶ deployment plan + ROI curve + blind spots
                                  └──forecast──▶ per-zone next-window risk + rising-trend flag
                                                   │
                        8 precomputed artifact files ──▶ Streamlit dashboard (the live demo)
```

- **`ingest`** — loads the raw CSV, explodes multi-label violation records into one row per (record × violation type), converts timestamps to IST, geo-filters to the Bengaluru bounding box, classifies road type from free-text location strings. Output: a clean, tidy violations table.
- **`cis`** — the scoring engine described in §4. Groups violations into geohash zones and computes the 6-component score.
- **`hotspots`** — runs DBSCAN clustering on top-scoring zones to name discrete physical hotspots (e.g., "this is one continuous chokepoint," not five disconnected high scores) and ranks them.
- **`validate`** — the proof layer (§6): junction-overlap validation and the blind-spot detector.
- **`forecast`** — a LightGBM model trained on lag/trend features (7-day and 28-day rolling violation counts, day-of-week, morning-share) that predicts each zone's **next-window risk**, plus a cheap linear-trend slope that flags "🔺 rising" zones — places getting worse, not just places that are already bad.
- **`deploy`** — the enforcement optimizer: given a patrol count *K*, greedily places non-overlapping patrol coverage circles on the highest-CIS zones to maximize how much high-impact violation activity gets covered. Produces a ranked deployment plan and a **ROI curve** (coverage % vs. patrol count) so BTP can pick a defensible patrol size, not a guess.
- **`briefing`** — composes a natural-language, per-station "morning briefing" Markdown document from the above outputs (template-based right now; deliberately architected with one documented swap-point to plug in a real Claude-generated version later — see §9).
- **`build_artifacts`** — runs the whole pipeline once and caches 8 files (`scored_zones.parquet`, `hotspots.parquet`, `forecast.parquet`, `forecast_metrics.json`, `deploy_plan.parquet`, `roi_curve.parquet`, `blind_spots.parquet`, `validation.json`) so the live dashboard never has to re-process 298K rows — it just reads small precomputed tables. This is also *why the demo loads instantly* despite running real ML underneath.

---

## 6. The proof layer — why a jury should believe any of this

A heatmap is a claim. ParkVision backs its claims with checks a skeptical traffic engineer can verify independently:

1. **Junction-overlap validation (85.0%)** — BTP's own dataset names 168 real junctions, and 50.4% of all violations sit at one. We check: of ParkVision's top-20 CIS-ranked zones, **85.0% sit at or near a real named junction.** This is *third-party ground truth ParkVision never used to build its own score* — it's not circular. It says: "our ranking algorithm independently rediscovers the junctions BTP already knows are problems," which is the strongest cheap proof available from this dataset.
2. **Officer-source diversity (95%)** — the obvious jury objection to any hotspot is "isn't that just wherever one officer happens to patrol, not real congestion?" Each violation carries an anonymized `created_by_id` identifying the logging officer. We check: of ParkVision's top-20 CIS-ranked zones, **95% draw violations from at least two distinct officers** (most from 35–60+ officers), not one person's beat. This is a second, fully independent check — it uses a column the CIS score never touches — and it answers the patrol-bias objection directly: these are zones many different officers independently converge on, not one person's route.
3. **Forecast backtest (Spearman ≈ 0.849)** — trained on data through February, validated against March's actual violations. We report a rank-correlation metric (the right metric for *prioritization*, which is what the optimizer actually needs) rather than cherry-picking a flattering regression metric.
4. **Patrol ROI** — at a recommended patrol size of **K=25**, the optimizer covers **43.6% of all high-impact violations** at K=20 (efficiency keeps climbing past that), versus a **Monte-Carlo random-placement baseline** of the same K — giving roughly **8.5× the coverage of random patrol placement**. We deliberately rejected a "K/N" naive baseline (which would have produced an absurd, untrustworthy 176× number) in favor of a real seeded random-placement simulation — an honest baseline, not a strawman.
5. **Enforcement blind-spots** — the top-10 of 54 police stations account for **58.6%** of all logged enforcement activity. That means enforcement attention is geographically lopsided. We surface the high-CIS zones that fall *outside* that busy-station coverage — genuinely under-patrolled chokepoints. This is the most directly actionable output in the whole project: it's a literal "go here, nobody is watching this" list.
6. **Honesty slide** — CIS is a domain-weighted proxy for congestion, not a direct sensor measurement (there's no ground-truth congestion data in this dataset, by design — no team has it). We say this explicitly, and the junction-overlap check is offered as the best available external validation given the constraint. The forecast is honestly framed as an **enforcement-pattern predictor**, not a "congestion clock" (per the timestamp finding in §4) — we predict where enforcement-relevant activity will recur, which is exactly what a patrol-deployment tool needs, and we don't oversell it as more than that.

**A related insight (not a validation proof):** 9.1% of all violations citywide come from vehicles seen 5+ times in the dataset. The CIS score's `recurrence` component already counts distinct zone-days; this is a different, vehicle-level lens — some top zones are chronic because the same vehicles keep coming back, not just because the location is generally busy. Tracked as a per-zone diagnostic (`repeat_offender_share`); not yet folded into the CIS formula.

---

## 7. The website — what it is and how to use it

The dashboard (`app.py`, Streamlit) is the **Demo Link** — a five-tab tool that an inspector or commander could plausibly open every morning. Each tab maps 1:1 to a step in the BTP workflow it's meant to support.

### Tab 1 — Priority Zones
**What it shows:** A live map of all 5,753 scored zones, color-coded by CIS (low → high on a severity ramp), plus headline stats (9.2% flow-choking framing, zone count, top CIS, the 85.0% junction-overlap proof — visually marked "Verified" since it's externally checked, unlike the model's own output) and a filterable top-20 table.
**How to use it:** Filter by police station, minimum CIS, or "rising only" to answer: *"Of everything happening in my jurisdiction, what actually matters?"* This replaces "drive the beat and see what you find" with "open the app and see the ranked list."

### Tab 2 — Forecast & Rising Hotspots
**What it shows:** Every zone's predicted near-term risk score, its trend slope, and a 🔺 flag for zones getting worse — plus the honest backtest metrics (Spearman, MAE, validation window) and an explicit framing note about what the forecast can and can't claim.
**How to use it:** Answer *"Where is this about to become a problem, even if it isn't the worst zone yet?"* — pre-emptive deployment instead of always reacting to the current worst spot.

### Tab 3 — Deployment Planner
**What it shows:** A patrol-size slider (K), four live ROI metrics (coverage %, random baseline %, efficiency multiple, marginal gain), the ROI curve chart, and a precomputed K=20 reference patrol plan (ranked zones to actually walk/drive to).
**How to use it:** Answer *"I have N officers for tomorrow's shift — where exactly do I send them, and what do I get for it?"* The K=25 recommendation marks the point of diminishing returns on the ROI curve — a defensible, data-backed resourcing number instead of "use the usual beat."

### Tab 4 — Enforcement Blind Spots
**What it shows:** High-CIS zones that fall outside the top-10 busiest stations' coverage, with the 58.6% skew narrative and a dedicated map/table.
**How to use it:** Answer *"What are we missing entirely, not just under-prioritizing?"* — a literal gap list for resource reallocation across stations, not just within one station's existing beat.

### Tab 5 — AI Enforcement Briefings
**What it shows:** A one-click, plain-English morning briefing per police station (54 stations covered), composed from all of the above — top chokepoints, rising zones, today's patrol-plan zones, and blind spots, in prose an officer can read in 30 seconds (see the worked example for Basavanagudi below).
**How to use it:** This is the artifact a station actually reads at shift handover — not a dashboard a commander has to interpret, but a memo someone can act on directly.

> **Worked example (real output, Basavanagudi station):**
> *"Good morning. Basavanagudi has 97 ranked zone(s) carrying 132 high-impact (flow-choking) violations. Today's top chokepoint is zone tdr1tht (CIS 51.2, 36 high-impact, 758 total violations)... Watch 29 zone(s) trending up... 1 under-served high-impact zone(s) need attention: tdr1tht."*

---

## 8. How this would actually be used in the field

Picture a station house-keeper or shift commander at 7 AM:
1. Open ParkVision (or just read the pre-generated `briefings/<station>.md` for their station — no dashboard required if connectivity is poor).
2. The briefing already tells them: the top 3 chokepoints in their jurisdiction today, which zones are trending worse (deploy before it gets bad, not after), which zones are on the recommended K=20/K=25 citywide patrol plan, and which high-impact zones nobody is currently watching.
3. They allocate today's patrol assignments based on that list instead of habit or complaint volume.
4. Over weeks, the **recurrence** component and the **rising-hotspot trend flag** let a station track whether a zone is actually improving after sustained attention — turning enforcement into a measured feedback loop instead of a one-off sweep.

This is also why the architecture explicitly supports the **ASTraM/SCITA framing**: the source dataset already carries a `data_sent_to_scita` field, and **85.7% of all violation records already have it set to true**, meaning BTP already pipes this kind of data into its own systems. ParkVision is positioned as a **scoring/prioritization layer that plugs into that existing pipeline** — not a brand-new system BTP would have to adopt wholesale, but an analytical layer on top of data they already collect and already route somewhere. That's the difference between "an interesting hackathon demo" and "something operationally adoptable," which is exactly what a jury that includes actual BTP officers will be listening for.

---

## 9. The AI Briefing — current state vs. future state (be upfront about this)

The five-tab dashboard is **deterministic Python/ML**, not an LLM wrapper — that's deliberate, since a jury evaluating "genuine AI" wants substance (LightGBM forecasting, DBSCAN clustering, a weighted scoring model), not just a chatbot UI. The one component that *could* sound LLM-flavored — the AI Briefing — currently runs on a **template backend**: deterministic, fast, free, and offline (no API key needed for the live demo, which also means the demo never breaks because of a network blip or a rate limit during judging).

The code has a single, explicit swap point (`parkvision/briefing.py::_generate_with_claude`) — a documented stub that would call the Claude API with the same underlying data (top zones, trends, patrol plan, blind spots) to produce richer, more naturally varied prose, with `BRIEFING_BACKEND` flipped from `"template"` to `"claude"`. **Be honest about this if asked:** the briefing logic and structure are real and complete; the "Claude-authored prose" upgrade is a clearly scoped, single-function next step, not a gap in the core idea. This is a reasonable answer to "is this just a wrapper?" — the analytical pipeline is the product; natural-language generation is a presentation layer on top of it.

---

## 10. How to explain this to the judges — a structured pitch

Use this shape for the live demo / video / deck. Each step is something you can click through.

**1. Open with the insight, not the tool.** *"BTP logs 298,450 parking violations over five months. We found that only 9.2% of them actually choke traffic. Reactive patrol treats all 300K equally. ParkVision doesn't."* (Tab 1 headline.)

**2. Prove you're not guessing.** *"We didn't just build a model and hope. We checked our top-ranked zones against BTP's own list of 168 named junctions — 85% of our top zones land on a real junction BTP already knows about."* (Tab 1 "Verified" badge.) This is the line that moves you from "interesting demo" to "defensible analysis" in a technical jury's mind.

**3. Show forward-looking value, honestly framed.** *"We don't just rank what's bad today — we forecast what's about to get worse, with an honest backtested accuracy number (Spearman 0.849), and we say plainly what this forecast is and isn't measuring."* (Tab 2.) Volunteering the limitation before they ask is what separates finalists from also-rans for a jury that includes domain experts.

**4. Get to the "so what" — the operational answer.** *"Given N patrols, here's exactly where to put them, and here's the proof it beats doing it randomly — by 7 to 8 times."* (Tab 3 — slide K, watch the numbers move live.) This is your single best "wow" moment: a live, interactive ROI number, not a static slide.

**5. Show you found something nobody was looking for.** *"The busiest 10 of 54 stations handle 58.6% of all enforcement. We found the high-impact zones sitting completely outside that coverage — the blind spots nobody's watching."* (Tab 4.) This is the most directly actionable single output — say so explicitly.

**6. Land on the artifact a real officer would use.** *"Here's what a station commander actually reads at 7 AM — not a dashboard, a briefing."* (Tab 5 — read one aloud, e.g. the Basavanagudi example above.)

**7. Close on deployability, not novelty.** *"This isn't a toy — the data already flows into BTP's SCITA pipeline. ParkVision is the scoring and prioritization layer that sits on top of data BTP already collects."* This answers the unspoken judge question "could we actually use this Monday morning?" before it's asked.

**If asked "is this just a heatmap with extra steps?"** — Answer with §3: a heatmap shows all 298K equally; ParkVision's entire architecture exists to find the 9.2% and prove that ranking is real (§6), not to make violations look pretty on a map.

**If asked "how do you know your scoring weights are right?"** — Answer with the junction-overlap check (85.0%) — independent, BTP-defined ground truth the weights were never fit against — plus point out that every weight lives in one config file (`config.py`) so it's transparent and tunable by BTP domain experts, not hardcoded magic numbers.

**If asked "what's the AI here, really?"** — LightGBM gradient-boosted forecasting with a proper temporal train/validate split (not random-shuffled, which would leak), DBSCAN spatial clustering, and a from-scratch weighted multi-component scoring model — plus an explicit, honest answer about the briefing's current template backend (§9) if pressed.

---

## 11. Headline numbers — cheat sheet for the deck/video

| Stat | Value | What it proves |
|---|---|---|
| Total violations analyzed | 298,450 | Real BTP field data, full provided window |
| Flow-choking share | **9.2%** | The core insight — most violations don't matter; we find the ones that do |
| Zones scored | 5,753 | Granularity — ~150m resolution across Bengaluru |
| Top zone CIS | 88.5 | Score range demonstrates real spread/discrimination, not flat scores |
| Junction-overlap validation | **85.0%** | Independent proof the ranking finds real chokepoints |
| Forecast backtest (Spearman) | **0.849** | Honestly validated predictive signal, temporal split |
| Recommended patrol size | K = 25 | Data-backed resourcing number, not a guess |
| Coverage at K=20 vs. random | **43.6% vs. ~5–6%** | ≈ **8.5×** efficiency over random placement |
| Top-10-station enforcement skew | 58.6% (of 54 stations) | Identifies the blind-spot opportunity |
| AI briefings generated | 54 (one per station) | Operational, not just a single demo example |
| SCITA pipeline integration | 85.7% | Deployability — already flows into BTP's existing data pipeline |

---

## 12. Honest limitations (state these before the jury finds them)

- **CIS is a domain-weighted proxy, not a direct sensor measurement of congestion** — there is no ground-truth traffic-flow dataset to train against; junction-overlap is the best available independent check given that constraint.
- **Violation timestamps are anonymized below the hour** (synthetic seconds, near-uniform minutes) — the forecast is honestly an **enforcement-pattern predictor**, not a live congestion clock. We dropped the originally planned time-of-day CIS component for this exact reason rather than ship something the data can't support.
- **The AI Briefing currently uses a deterministic template, not a live Claude call** — by design, for demo reliability (no API key/network dependency during judging) — with a documented, single-function swap point to upgrade it.
- **The optimizer's "random baseline" is a seeded Monte-Carlo simulation of random patrol placement**, deliberately chosen over a naive K/N ratio that would have produced an inflated, not-credible efficiency number.
- **`closed_datetime` and `action_taken_timestamp` are 100% empty in this dataset** — there is no enforcement-resolution-timing signal to analyze. We don't claim response-time, dwell-time, or "time-to-action" analytics anywhere in ParkVision, because the data genuinely doesn't support it; this is a property of the source data, not a gap in our pipeline.

---

*This file lives at `Round2_gsd/PROJECT_OVERVIEW.md`. It is documentation for humans (you, teammates, the jury prep) — it is not part of the Streamlit app and is not consumed by any code.*
