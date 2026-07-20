from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_periodos_y_dashboard_por_upload(admin_token):
    with open("tests/fixtures/pmk_sample.xlsx", "rb") as f:
        r = client.post("/api/uploads", files={"file": ("pmk.xlsx", f)},
                        headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 201
    up = r.json()
    assert up["periodo"] == "2026-07"

    p = client.get("/api/periodos", headers={"Authorization": f"Bearer {admin_token}"})
    assert p.status_code == 200
    meses = [x["periodo"] for x in p.json()]
    assert "2026-07" in meses

    d = client.get(f"/api/dashboard?upload_id={up['upload_id']}", headers={"Authorization": f"Bearer {admin_token}"})
    assert d.status_code == 200
    assert d.json()["kpis"]["ventaTotalUF"] > 0
    assert d.json()["semana"]
