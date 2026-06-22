from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import app, HealthResponse, ZoneRow, HotspotRow
from api.main import (
    ForecastRow, DeployPlanRow, DeployPlanResponse, BlindSpotRow, ValidationResponse,
)


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


class TestHealth:
    def test_health_200(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert set(body.keys()) == {"status", "artifacts_loaded", "version"}
        assert body["artifacts_loaded"] is True
        HealthResponse(**body)

    def test_debug_is_off(self):
        assert app.debug is False


@pytest.fixture()
def known_zone_id(client) -> str:
    r = client.get("/zones", params={"top_n": 1})
    assert r.status_code == 200
    return r.json()[0]["zone_id"]


class TestZones:
    def test_zones_schema_and_cap(self, client):
        r = client.get("/zones", params={"top_n": 5})
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, list) and len(body) == 5
        for row in body:
            ZoneRow(**row)
        cis_values = [row["cis"] for row in body]
        assert cis_values == sorted(cis_values, reverse=True)

    def test_zones_min_cis_filter(self, client):
        r = client.get("/zones", params={"top_n": 50, "min_cis": 40})
        assert r.status_code == 200
        assert all(row["cis"] >= 40 for row in r.json())

    def test_zones_top_n_out_of_range(self, client):
        assert client.get("/zones", params={"top_n": 0}).status_code == 422
        assert client.get("/zones", params={"top_n": 99999}).status_code == 422

    def test_zones_unknown_zone_id_404(self, client):
        assert client.get("/zones", params={"zone_id": "NOTAZONE"}).status_code == 404

    def test_zones_known_zone_id_200(self, client, known_zone_id):
        r = client.get("/zones", params={"zone_id": known_zone_id})
        assert r.status_code == 200
        assert len(r.json()) == 1
        assert r.json()[0]["zone_id"] == known_zone_id

    def test_zones_no_pii_columns(self, client):
        row = client.get("/zones", params={"top_n": 1}).json()[0]
        for forbidden in ("vehicle_number", "created_by_id", "device_id"):
            assert forbidden not in row

    def test_zones_id_overrides_min_cis_filter(self, client, known_zone_id):
        """zone_id lookup should ignore min_cis filter — verify zone is returned
        even if its CIS is below the min_cis threshold."""
        r = client.get(
            "/zones",
            params={"zone_id": known_zone_id, "min_cis": 99}
        )
        assert r.status_code == 200
        body = r.json()
        assert len(body) == 1
        assert body[0]["zone_id"] == known_zone_id

    def test_zones_min_cis_excludes_all_returns_empty_200(self, client):
        """when min_cis is set so high no zones qualify, bulk-list path should
        return 200 with empty list [], not 404."""
        r = client.get("/zones", params={"top_n": 50, "min_cis": 100.0})
        assert r.status_code == 200
        assert r.json() == []


class TestHotspots:
    def test_hotspots_schema_and_cap(self, client):
        r = client.get("/hotspots", params={"top_n": 5})
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, list) and len(body) <= 5
        for row in body:
            HotspotRow(**row)

    def test_hotspots_top_n_out_of_range(self, client):
        assert client.get("/hotspots", params={"top_n": 0}).status_code == 422
        assert client.get("/hotspots", params={"top_n": 9999}).status_code == 422


class TestForecast:
    def test_forecast_schema_and_cap(self, client):
        r = client.get("/forecast", params={"top_n": 10})
        assert r.status_code == 200
        for row in r.json():
            ForecastRow(**row)

    def test_forecast_rising_only(self, client):
        r = client.get("/forecast", params={"top_n": 100, "rising_only": True})
        assert r.status_code == 200
        assert all(row["rising"] is True for row in r.json())


class TestDeployPlan:
    def test_deploy_plan_schema(self, client):
        r = client.get("/deploy-plan")
        assert r.status_code == 200
        body = DeployPlanResponse(**r.json())
        assert len(body.plan) > 0
        assert body.recommended_k == 25


class TestBlindSpots:
    def test_blind_spots_schema(self, client):
        r = client.get("/blind-spots")
        assert r.status_code == 200
        for row in r.json():
            BlindSpotRow(**row)


class TestValidation:
    def test_validation_schema(self, client):
        r = client.get("/validation")
        assert r.status_code == 200
        body = ValidationResponse(**r.json())
        assert 0.0 <= body.overlap_pct <= 100.0


class TestErrorResponseIsGeneric:
    def test_error_response_no_traceback(self, monkeypatch):
        import api.main as main_module

        def _boom(*args, **kwargs):
            raise RuntimeError(
                "/Users/sak/Desktop/MSI WORK/GriDLocK/Round2_gsd/artifacts/secret leaked"
            )

        # Force the catch-all by breaking the row serializer used by /zones.
        monkeypatch.setattr(main_module, "_rows", _boom)
        with TestClient(app, raise_server_exceptions=False) as unsafe:
            r = unsafe.get("/zones", params={"top_n": 5})
        assert r.status_code == 500
        assert r.json() == {"detail": "internal error"}
        text = r.text
        for leak in ("Traceback", "secret", "/Users/", "RuntimeError", "artifacts"):
            assert leak not in text
