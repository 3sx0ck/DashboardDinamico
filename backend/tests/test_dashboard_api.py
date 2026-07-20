from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_upload_y_dashboard(admin_token):
    with open("tests/fixtures/pmk_sample.xlsx", "rb") as f:
        r = client.post("/api/uploads", files={"file": ("pmk.xlsx", f)},
                        headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 201
    upload_data = r.json()
    assert "upload_id" in upload_data
    assert upload_data["periodo"] == "2026-07"

    d = client.get("/api/dashboard", headers={"Authorization": f"Bearer {admin_token}"})
    assert d.status_code == 200
    dashboard_data = d.json()
    assert dashboard_data["periodo"] == "2026-07"
    assert dashboard_data["kpis"]["ventaTotalUF"] > 0
