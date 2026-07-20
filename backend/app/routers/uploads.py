import uuid
import tempfile
import os
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.db import get_db
from app import models
from app.auth.deps import require_admin
from app.storage import put_raw
from app.parser.pmk_parser import parse_pmk
from app.persist import persist_parsed

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

# Modelos de dominio ligados a un periodo (se reemplazan al re-subir un periodo).
_DOMAIN_MODELS = [
    models.Venta, models.Stock, models.Funnel, models.EvolucionMensual,
    models.Canal, models.MarketingMedio, models.MarketingBanco,
    models.MarketingKpis, models.AvanceSemanal, models.GrillaUnidad,
]


def _clear_snapshot(db: Session, periodo: str, semana: str):
    """Borra datos previos del mismo snapshot (periodo+semana) para que
    re-subir la misma semana reemplace, pero una semana distinta acumule."""
    upload_ids = [
        row.id for row in db.query(models.Upload.id)
        .filter(models.Upload.periodo == periodo, models.Upload.semana == semana)
        .all()
    ]
    if not upload_ids:
        return
    for M in _DOMAIN_MODELS:
        db.query(M).filter(M.upload_id.in_(upload_ids)).delete(synchronize_session=False)
    db.query(models.Upload).filter(models.Upload.id.in_(upload_ids)).delete(synchronize_session=False)
    db.commit()


@router.post("", status_code=201)
async def upload(file: UploadFile = File(...), db: Session = Depends(get_db),
                 admin: models.User = Depends(require_admin)):
    raw = await file.read()
    uid = uuid.uuid4().hex
    key = f"pmk/{uid}/{file.filename}"
    put_raw(key, raw)

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp.write(raw)
        tmp_path = tmp.name

    try:
        data = parse_pmk(tmp_path)
    finally:
        os.unlink(tmp_path)

    periodo = data["meta"]["periodo"]
    semana = data["meta"].get("semana", "")
    fecha = data["meta"].get("fecha")
    _clear_snapshot(db, periodo, semana)
    up = models.Upload(periodo=periodo, semana=semana, fecha=fecha,
                       filename=file.filename, bucket_key=key, uploaded_by=admin.id)
    db.add(up)
    db.commit()
    db.refresh(up)
    persist_parsed(db, up, data)

    return {"upload_id": up.id, "periodo": periodo, "semana": semana, "fecha": fecha}
