import pandas as pd

def junction_overlap(scored_zones, top_n=20, thresh=0.5):
    top = scored_zones.head(top_n)
    n = len(top)
    if n == 0:
        return {"top_n": top_n, "overlap_pct": 0.0, "n_top_zones": 0}
    overlap = (top["junction_prox"] >= thresh).mean() * 100
    return {"top_n": top_n, "overlap_pct": round(float(overlap), 1), "n_top_zones": int(n)}
