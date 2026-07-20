from app.parser.pmk_parser import parse_pmk
from app.persist import persist_parsed
from app.db import SessionLocal
from app import models


def test_persist_cuenta(seed_admin):
    db = SessionLocal()
    # Clean up before test
    for M in [models.Funnel, models.Canal, models.Venta, models.Stock, models.EvolucionMensual,
              models.MarketingMedio, models.MarketingBanco, models.MarketingKpis,
              models.AvanceSemanal, models.GrillaUnidad]:
        db.query(M).delete()
    db.query(models.Upload).delete()
    db.commit()

    # Get the seeded admin user
    admin = db.query(models.User).filter_by(email="admin@example.com").first()
    assert admin is not None, "Admin user not found"

    # Create upload record
    up = models.Upload(periodo="2026-07", filename="f.xlsx", bucket_key="k", uploaded_by=admin.id)
    db.add(up)
    db.commit()
    db.refresh(up)

    # Parse and persist
    data = parse_pmk("tests/fixtures/pmk_sample.xlsx")
    persist_parsed(db, up, data)

    # Verify counts
    assert db.query(models.Canal).count() == 2
    assert db.query(models.GrillaUnidad).count() > 0
    db.close()
