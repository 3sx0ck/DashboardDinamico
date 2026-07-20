from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_login_ok(seed_admin):
    r = client.post("/api/auth/login", data={"username": "admin@example.com", "password": "admin1234"})
    assert r.status_code == 200
    assert r.json()["rol"] == "admin"

def test_admin_crea_visitante(admin_token):
    r = client.post("/api/users", json={"email":"v@example.com","nombre":"V","password":"x","rol":"visitante"},
                    headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 201

def test_visitante_no_crea_usuarios(admin_token):
    client.post("/api/users", json={"email":"v2@example.com","nombre":"V","password":"x","rol":"visitante"},
                headers={"Authorization": f"Bearer {admin_token}"})
    vc = client.post("/api/auth/login", data={"username": "v2@example.com", "password": "x"})
    vtok = vc.json()["access_token"]
    r = client.post("/api/users", json={"email":"z@example.com","nombre":"Z","password":"x","rol":"visitante"},
                    headers={"Authorization": f"Bearer {vtok}"})
    assert r.status_code == 403
