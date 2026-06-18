import pandas as pd
import pytest

@pytest.fixture
def raw_csv(tmp_path):
    """A tiny CSV mirroring the real columns we use."""
    rows = [
        # in-bbox, two labels -> explodes to 2 rows; 02:30 UTC -> 08:00 IST
        {"id": "A", "latitude": 12.97, "longitude": 77.59,
         "violation_type": '["WRONG PARKING","PARKING IN A MAIN ROAD"]',
         "vehicle_type": "CAR", "junction_name": "BTP082 - KR Market Junction",
         "location": "18th Main Road, Block 2, Koramangala, Bengaluru",
         "police_station": "City Market", "validation_status": "approved",
         "created_datetime": "2024-01-15 02:30:00+00"},
        # in-bbox, single label; 18:00 UTC -> 23:30 IST
        {"id": "B", "latitude": 12.93, "longitude": 77.62,
         "violation_type": '["NO PARKING"]',
         "vehicle_type": "SCOOTER", "junction_name": "No Junction",
         "location": "6th Cross Road, Madiwala, Bengaluru",
         "police_station": "Madiwala", "validation_status": "NULL",
         "created_datetime": "2024-01-15 18:00:00+00"},
        # OUT of bbox -> must be dropped
        {"id": "C", "latitude": 0.0, "longitude": 0.0,
         "violation_type": '["NO PARKING"]',
         "vehicle_type": "CAR", "junction_name": "No Junction",
         "location": "Somewhere, Nowhere",
         "police_station": "X", "validation_status": "NULL",
         "created_datetime": "2024-01-15 05:00:00+00"},
    ]
    p = tmp_path / "mini.csv"
    pd.DataFrame(rows).to_csv(p, index=False)
    return p
