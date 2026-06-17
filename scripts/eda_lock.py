"""Phase-0 lock: prints the pitch headline numbers and resolves the timezone question."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from parkvision import ingest, config

def main():
    df = ingest.load_violations()
    HIGH = {k for k, v in config.SEVERITY_WEIGHTS.items() if v == 1.0}
    by_id_v = df.groupby("id")["violation"]
    high = by_id_v.apply(lambda s: bool(set(s) & HIGH)).mean() * 100
    junc = (df.groupby("id")["junction_name"].first().fillna("No Junction") != "No Junction").mean() * 100
    top10 = df.groupby("id")["police_station"].first().value_counts()
    top10share = top10.head(10).sum() / top10.sum() * 100

    print(f"records (unique ids):      {df['id'].nunique():,}")
    print(f"exploded violation rows:   {len(df):,}")
    print(f"HIGH-impact share:         {high:.1f}%   (expect ~9.2)")
    print(f"at named junction:         {junc:.1f}%   (expect ~50.5)")
    print(f"top-10/{df['police_station'].nunique()} station share: {top10share:.1f}%   (expect ~58.6)")
    print("\nIST hour histogram (confirm peak windows for config.PEAK_HOURS_IST):")
    print(df.groupby("id")["hour"].first().value_counts().sort_index().to_string())

if __name__ == "__main__":
    main()
