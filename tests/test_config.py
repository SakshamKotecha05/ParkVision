from parkvision import config

def test_cis_weights_sum_to_one():
    assert abs(sum(config.CIS_WEIGHTS.values()) - 1.0) < 1e-9

def test_severity_known_and_default():
    assert config.severity_weight("PARKING NEAR ROAD CROSSING") == 1.0
    assert config.severity_weight("WRONG PARKING") == 0.6
    assert config.severity_weight("DEFECTIVE NUMBER PLATE") == 0.1
    # rare/unlisted label -> default 0.0 (total map, nothing drops)
    assert config.severity_weight("JUMPING TRAFFIC SIGNAL") == 0.0
    assert config.severity_weight("anything else") == config.DEFAULT_WEIGHT

def test_vehicle_footprint_known_and_default():
    assert config.vehicle_footprint("HGV") == 1.0
    assert config.vehicle_footprint("SCOOTER") == 0.2
    assert config.vehicle_footprint("UNSEEN") == config.DEFAULT_FOOTPRINT

def test_data_path_points_at_csv():
    assert config.DATA_PATH.name.endswith(".csv")
