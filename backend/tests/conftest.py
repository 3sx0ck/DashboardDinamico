import pytest
from app.db import SessionLocal
from app import models
from app.auth.security import hash_password

@pytest.fixture
def seed_admin():
    db = SessionLocal()
    # Clean up all dependent tables before deleting users
    for M in [models.Funnel, models.Canal, models.Venta, models.Stock, models.EvolucionMensual,
              models.MarketingMedio, models.MarketingBanco, models.MarketingKpis,
              models.AvanceSemanal, models.GrillaUnidad, models.Upload]:
        db.query(M).delete()
    db.query(models.User).delete()
    db.commit()
    db.add(models.User(email="admin@example.com", nombre="A",
                       password_hash=hash_password("admin1234"), rol="admin"))
    db.commit(); db.close()
    yield

@pytest.fixture
def admin_token(seed_admin):
    from fastapi.testclient import TestClient
    from main import app
    c = TestClient(app)
    r = c.post("/api/auth/login", data={"username": "admin@example.com", "password": "admin1234"})
    return r.json()["access_token"]
