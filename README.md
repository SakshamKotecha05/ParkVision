# ParkVision

Congestion-Impact ranking for Bengaluru parking-violation enforcement.
ParkVision scores ~5,750 zones by a Congestion-Impact Score (CIS), forecasts
rising hotspots, plans patrol deployments, and surfaces enforcement blind
spots — exposed through a Streamlit dashboard with per-station AI briefings.

Only ~9.2% of the ~298,450 logged violations actually choke traffic flow.
ParkVision finds that 9.2% so enforcement effort lands where it matters.

## Instructions to Run (local)

All commands use the project's Python interpreter; quote the path (it has a
space).

1. Install dependencies:

   ```bash
   /opt/anaconda3/bin/python -m pip install -r requirements.txt
   ```

2. Place the provided source CSV at the project root (only needed to rebuild
   artifacts — the dashboard itself reads `artifacts/`, not the CSV):

   `jan to may police violation_anonymized791b166.csv`

3. (Optional) Regenerate the cached artifacts if `artifacts/` is missing:

   ```bash
   /opt/anaconda3/bin/python -m parkvision.build_artifacts
   ```

4. Pre-generate the per-station AI briefings (writes `briefings/*.md`):

   ```bash
   /opt/anaconda3/bin/python -c "from parkvision.briefing import generate_all_briefings; generate_all_briefings()"
   ```

5. Launch the dashboard:

   ```bash
   /opt/anaconda3/bin/python -m streamlit run app.py
   ```

   Open the URL Streamlit prints (default http://localhost:8501).

## Deploy (Streamlit Community Cloud — live Demo Link)

The live demo reads only the cached artifacts and briefings, never the 109 MB
source CSV, and needs no API key.

1. Create a public GitHub repo and push this project to it.
2. **Important — ship the artifacts and briefings.** `.gitignore` excludes
   `artifacts/`, `*.parquet`, and `briefings/`, and the source CSV exceeds
   GitHub's 100 MB limit. The deployed app needs the small artifact and
   briefing files (a few hundred KB total), so for the deploy commit, force-add
   them:

   ```bash
   git add -f artifacts/*.parquet artifacts/*.json briefings/*.md requirements.txt app.py parkvision/
   ```

   Do NOT commit the source CSV. (Your normal local `.gitignore` stays as-is;
   this force-add is only to include the small read-only artifacts the live app
   serves.)
3. On https://share.streamlit.io, create a new app pointing at:
   - **Repository:** your public repo
   - **Branch:** your default branch
   - **Main file path:** `app.py`
   - **Requirements:** `requirements.txt` (auto-detected at repo root)
4. Deploy. The app boots, `parkvision.app_data.load_all()` reads the committed
   artifacts, and the AI Briefings tab reads the committed `briefings/*.md`
   (falling back to live template generation if any file is missing).
5. Use the resulting `https://<app>.streamlit.app` URL as the submission's
   Demo Link.

## Architecture

- `parkvision/` — modelling pipeline (Plans 1 & 2): ingest, CIS scoring,
  hotspots, forecast, deploy optimizer, validation, `build_artifacts.py`.
- `artifacts/` — 8 pre-built read-only files the dashboard consumes.
- `parkvision/app_data.py` — cached artifact loader.
- `parkvision/dashboard/` — one render module per dashboard tab.
- `parkvision/briefing.py` — template-composed per-station briefings (single
  documented swap point for a future Claude backend).
- `app.py` — Streamlit entrypoint.
