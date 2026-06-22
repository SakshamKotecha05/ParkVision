from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # Round2_gsd/
DATA_PATH = ROOT / "jan to may police violation_anonymized791b166.csv"
ARTIFACTS = ROOT / "artifacts"

GEOHASH_PRECISION = 7          # ~150 m cells
IST = "Asia/Kolkata"
BBOX = {"lat_min": 12.7, "lat_max": 13.3, "lon_min": 77.4, "lon_max": 77.8}

# Severity tiers — exact dataset strings (incl. misspellings). Total via DEFAULT_WEIGHT.
SEVERITY_WEIGHTS = {
    # High (chokes carriageway/junction) = 1.0
    "PARKING NEAR ROAD CROSSING": 1.0,
    "PARKING NEAR TRAFFIC LIGHT OR ZEBRA CROSS": 1.0,
    "PARKING IN A MAIN ROAD": 1.0,
    "PARKING NEAR BUSTOP/SCHOOL/HOSPITAL ETC": 1.0,
    "DOUBLE PARKING": 1.0,
    "PARKING OPPOSITE TO ANOTHER PARKED VEHICLE": 1.0,
    "H T V PROHIBITED": 1.0,
    "AGAINST ONE WAY/NO ENTRY": 1.0,
    "VIOLATING LANE DISIPLINE": 1.0,
    # Medium (obstructs/spillover) = 0.6
    "WRONG PARKING": 0.6,
    "NO PARKING": 0.6,
    "PARKING ON FOOTPATH": 0.6,
    "PARKING OTHER THAN BUS STOP": 0.6,
    # Low (~no flow impact) = 0.1
    "DEFECTIVE NUMBER PLATE": 0.1,
    "USING BLACK FILM/OTHER MATERIALS": 0.1,
    "WITHOUT SIDE MIRROR": 0.1,
    "REFUSE TO GO FOR HIRE": 0.1,
    "DEMANDING EXCESS FARE": 0.1,
    "FAIL TO USE SAFETY BELTS": 0.1,
    "OBSTRUCTING DRIVER": 0.1,
}
DEFAULT_WEIGHT = 0.0           # any unlisted/rare non-parking label

VEHICLE_FOOTPRINT = {          # lane-width proxy
    "HGV": 1.0, "LORRY/GOODS VEHICLE": 1.0, "BUS (BMTC/KSRTC)": 1.0,
    "PRIVATE BUS": 1.0, "TEMPO": 0.8, "LGV": 0.7, "GOODS AUTO": 0.6,
    "CAR": 0.5, "MAXI-CAB": 0.5, "VAN": 0.5, "JEEP": 0.5,
    "PASSENGER AUTO": 0.4, "MOTOR CYCLE": 0.2, "SCOOTER": 0.2, "MOPED": 0.2,
}
DEFAULT_FOOTPRINT = 0.3

# Road-class congestion weight (0–1): how much a blocked lane on this class hurts flow.
# road_type is derived from the `location` text by ingest.classify_road_type (~97.5% classified).
ROAD_WEIGHTS = {
    "arterial": 1.0,     # highway / ring road / flyover / NH / expressway
    "main": 0.7,         # main road
    "road": 0.5,         # generic named road
    "cross": 0.4,        # grid cross-street
    "residential": 0.2,  # block / layout / colony / nagar
    "unknown": 0.4,
}
DEFAULT_ROAD_WEIGHT = 0.4

CIS_WEIGHTS = {                # must sum to 1.0
    "severity": 0.35, "density": 0.25, "junction": 0.15,
    "roadtype": 0.10, "vehicle": 0.10, "recurrence": 0.05,
}

# LOCKED in Task 3 against the real IST hour distribution (298,450 records).
# The data is a single unimodal *morning enforcement* block peaking 10–11 IST;
# 08–11 IST = 39.4% of all records. There is NO evening peak (17–21 IST = 0.2%),
# so the provisional rush-hour evening window was dropped.
# NOTE: created_datetime is anonymization-synthesized below hour granularity
# (100% of seconds == :46, minutes ~uniform) — hour-of-day is the finest
# trustworthy resolution, and reflects enforcement logging, not live congestion.
PEAK_HOURS_IST = {8, 9, 10, 11}


def severity_weight(label: str) -> float:
    return SEVERITY_WEIGHTS.get(label, DEFAULT_WEIGHT)


def vehicle_footprint(vtype: str) -> float:
    return VEHICLE_FOOTPRINT.get(vtype, DEFAULT_FOOTPRINT)


def road_weight(road_type: str) -> float:
    return ROAD_WEIGHTS.get(road_type, DEFAULT_ROAD_WEIGHT)
