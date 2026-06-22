import pandas as pd
import pytest

from parkvision import briefing


def _fixtures():
    scored_zones = pd.DataFrame({
        "zone_id": ["z1", "z2", "z3"],
        "station": ["Indiranagar", "Indiranagar", "Koramangala"],
        "cis": [88.5, 70.1, 55.0],
        "high_impact": [9, 4, 2],
        "n_violations": [120, 60, 30],
        "lat": [12.97, 12.96, 12.93],
        "lon": [77.64, 77.63, 77.62],
    })
    forecast = pd.DataFrame({
        "zone_id": ["z1", "z2", "z3"],
        "risk": [10.0, 5.0, 3.0],
        "slope": [0.4, -0.1, 0.2],
        "rising": [True, False, True],
    })
    deploy_plan = pd.DataFrame({
        "rank": [1], "zone_id": ["z1"], "lat": [12.97], "lon": [77.64],
        "cis": [88.5], "high_impact_covered": [9], "cis_covered": [88.5],
        "n_zones_covered": [1],
    })
    blind_spots = pd.DataFrame({
        "zone_id": ["z3"], "lat": [12.93], "lon": [77.62], "cis": [55.0],
        "high_impact": [2], "n_violations": [30], "station": ["Koramangala"],
        "busy_station": [False], "blindspot_rank": [1],
    })
    return scored_zones, forecast, deploy_plan, blind_spots


def test_slugify_handles_spaces_and_punctuation():
    assert briefing.slugify("Indiranagar") == "indiranagar"
    assert briefing.slugify("K.R. Puram Traffic PS") == "kr_puram_traffic_ps"
    assert briefing.slugify("Hal/HSR  Layout") == "halhsr_layout"


def test_make_briefing_returns_prose_with_station_and_zone():
    sz, fc, dp, bs = _fixtures()
    out = briefing.make_briefing("Indiranagar", sz, fc, dp, bs)
    assert isinstance(out, str) and len(out) > 50
    assert "Indiranagar" in out
    # contains at least one zone_id belonging to that station
    assert "z1" in out
    # reads like prose, not a JSON dump
    assert "{" not in out and "}" not in out


def test_make_briefing_mentions_rising_and_blind_spots_when_present():
    sz, fc, dp, bs = _fixtures()
    out = briefing.make_briefing("Koramangala", sz, fc, dp, bs)
    assert "Koramangala" in out
    assert "z3" in out  # its rising zone / blind spot


def test_generate_all_briefings_writes_one_md_per_station(tmp_path):
    sz, fc, dp, bs = _fixtures()
    paths = briefing.generate_all_briefings(
        out_dir=tmp_path, scored_zones=sz, forecast=fc,
        deploy_plan=dp, blind_spots=bs)
    written = sorted(p.name for p in tmp_path.glob("*.md"))
    assert written == ["indiranagar.md", "koramangala.md"]
    assert len(paths) == 2
    text = (tmp_path / "indiranagar.md").read_text()
    assert "Indiranagar" in text


def test_claude_backend_without_anthropic_raises_notimplemented():
    sz, fc, dp, bs = _fixtures()
    with pytest.raises(NotImplementedError) as exc:
        briefing.make_briefing("Indiranagar", sz, fc, dp, bs, backend="claude")
    assert "anthropic" in str(exc.value).lower()
