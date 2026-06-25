# ParkVision

Congestion impact ranking for Bengaluru's parking enforcement, built for Flipkart Gridlock 2.0, Theme 1: poor visibility on parking induced congestion.

BTP logs roughly 298,450 parking violation records across the city. Only 9.2% of them actually choke traffic flow: a double-parked truck at a road crossing matters, a defective number plate doesn't. ParkVision scores every ~150m zone in Bengaluru on a 0 to 100 Congestion Impact Score, clusters the worst zones into named hotspots, forecasts which ones are about to get worse, and hands a shift commander a ranked patrol plan, all through a Streamlit dashboard with one click briefings per station.

## Submission

Prototype Phase submitted ahead of the 23 Jun 2026 deadline.

* Live demo: https://parkvision-20.streamlit.app/
* Repository: https://github.com/SakshamKotecha05/ParkVision
* Full writeup, headline numbers, and pitch: `ProjectDetail.md`
* Dashboard user guide: `HOW_TO_USE.md`
* Deck prompt, video script, and form fields: `SUBMISSION.md`

## Run it locally

All commands use the project's Python interpreter. Quote the path; it contains a space.

1. Install dependencies:

   ```bash
   /opt/anaconda3/bin/python -m pip install -r requirements.txt
   ```

2. Place the provided source CSV at the project root. It's only needed to rebuild artifacts; the dashboard itself reads `artifacts/`, never the CSV directly.

   `jan to may police violation_anonymized791b166.csv`

3. Regenerate the cached artifacts if `artifacts/` is missing:

   ```bash
   /opt/anaconda3/bin/python -m parkvision.build_artifacts
   ```

4. Generate the per station AI briefings ahead of time. This writes `briefings/*.md`:

   ```bash
   /opt/anaconda3/bin/python -c "from parkvision.briefing import generate_all_briefings; generate_all_briefings()"
   ```

5. Launch the dashboard:

   ```bash
   /opt/anaconda3/bin/python -m streamlit run app.py
   ```

   Open the URL Streamlit prints (default `http://localhost:8501`).

Run the test suite with `/opt/anaconda3/bin/python -m pytest`.

## Deploy on Streamlit Community Cloud

The live demo reads only the cached artifacts and briefings, never the 109 MB source CSV, and needs no API key.

1. Push this project to a public GitHub repo.
2. Ship the artifacts and briefings. `.gitignore` excludes `artifacts/*`, `*.parquet`, and `briefings/` by default since the source CSV exceeds GitHub's 100 MB limit, but the eight read only artifact files the app needs are listed as explicit exceptions (see the `!artifacts/...` lines). Briefings still need a force add:

   ```bash
   git add -f briefings/*.md
   ```

   Never commit the source CSV.
3. On https://share.streamlit.io, create a new app: repository = your repo, branch = your default branch, main file path = `app.py`. Requirements at `requirements.txt` are auto detected.
4. Deploy. `parkvision.app_data.load_all()` reads the committed artifacts on boot; the AI Briefings tab reads the committed `briefings/*.md`, falling back to live template generation if a file is missing.

## Architecture

```
CSV -> ingest -> tidy violations -> cis -> scored zones -> hotspots -> named hotspots
                                              |
                                              +-> deploy -> deployment plan, ROI curve, blind spots
                          forecast -> each zone's risk for the next window, rising trend flag
                                              |
              8 cached artifacts -> Streamlit dashboard (app.py)
                                 -> FastAPI read only serving layer (api/)
```

* `parkvision/`: the modelling pipeline. `ingest.py`, `cis.py`, `hotspots.py`, `forecast.py`, `deploy.py`, `validate.py`, `sensitivity.py`, `briefing.py`, `build_artifacts.py`.
* `parkvision/app_data.py`: cached loader for the eight artifact files.
* `parkvision/dashboard/`: one render module per Streamlit tab.
* `artifacts/`: the read only files the dashboard and API consume.
* `briefings/`: 54 Markdown briefings, one per station, generated in advance.
* `api/`: FastAPI serving layer over the same artifacts, with `api/Dockerfile` for containerized deploys.
* `app.py`: the Streamlit entrypoint.
* `tests/`: pytest suite covering ingest, CIS, forecast, deploy, the API, and integration paths.
