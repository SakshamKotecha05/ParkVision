import json
from pathlib import Path
from . import ingest, cis, hotspots, validate
from .config import ARTIFACTS, DATA_PATH

def build(out_dir=ARTIFACTS, data_path=DATA_PATH) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    violations = ingest.load_violations(data_path)
    zones = cis.score_zones(violations)
    zones_h = hotspots.detect_hotspots(zones)
    val = validate.junction_overlap(zones_h)

    zones_h.to_parquet(out / "scored_zones.parquet", index=False)
    hotspots.rank_hotspots(zones_h, top_n=50).to_parquet(out / "hotspots.parquet", index=False)
    (out / "validation.json").write_text(json.dumps(val, indent=2))

    return {"n_zones": int(len(zones_h)),
            "top_cis": float(zones_h["cis"].max()) if len(zones_h) else 0.0,
            "overlap_pct": val["overlap_pct"]}

if __name__ == "__main__":
    print(build())
