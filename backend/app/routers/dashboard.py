from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app import models
from app.auth.deps import current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])
periodos_router = APIRouter(prefix="/api/periodos", tags=["periodos"])


@periodos_router.get("")
def periodos(db: Session = Depends(get_db), _: models.User = Depends(current_user)):
    uploads = db.query(models.Upload).all()
    grouped: dict[str, list] = {}
    for up in uploads:
        grouped.setdefault(up.periodo, []).append(up)

    result = []
    for periodo in sorted(grouped.keys(), reverse=True):
        weeks = sorted(grouped[periodo], key=lambda u: (u.fecha or ""), reverse=True)
        result.append({
            "periodo": periodo,
            "weeks": [{"uploadId": w.id, "semana": w.semana, "fecha": w.fecha} for w in weeks],
        })
    return result


def _resolve_upload(db: Session, periodo: Optional[str], upload_id: Optional[int]):
    if upload_id:
        return db.get(models.Upload, upload_id)
    q = db.query(models.Upload)
    if periodo:
        q = q.filter(models.Upload.periodo == periodo)
    try:
        return q.order_by(models.Upload.fecha.desc().nullslast(),
                          models.Upload.created_at.desc()).first()
    except Exception:
        return q.order_by(models.Upload.created_at.desc()).first()


@router.get("")
def dashboard(periodo: Optional[str] = None, upload_id: Optional[int] = None, torre: Optional[int] = None,
              db: Session = Depends(get_db), _: models.User = Depends(current_user)):
    up = _resolve_upload(db, periodo, upload_id)
    if not up:
        return {"empty": True, "periodo": None}

    def q(M):
        query = db.query(M).filter(M.upload_id == up.id)
        if torre and hasattr(M, "torre"):
            query = query.filter(M.torre == torre)
        return query.all()

    funnel = db.query(models.Funnel).filter_by(upload_id=up.id).first()
    ventas = q(models.Venta)
    stock = q(models.Stock)

    return {
        "periodo": up.periodo,
        "semana": up.semana,
        "fecha": up.fecha,
        "uploadId": up.id,
        "kpis": {
            "ventaTotalUF": sum(v.venta_uf for v in ventas),
            "xRecibirUF": sum(v.x_recibir_uf for v in ventas),
            "escriturados": sum(v.escriturados for v in ventas),
        },
        "funnel": None if not funnel else {
            "ofertas": funnel.ofertas, "desistidos": funnel.desistidos,
            "enCurso": funnel.en_curso, "promesas": funnel.promesas, "escrituras": funnel.escrituras
        },
        "ventas": [{"torre": v.torre, "ventaUF": v.venta_uf, "xRecibirUF": v.x_recibir_uf} for v in ventas],
        "stock": [{"torre": s.torre, "tipologia": s.tipologia, "disponible": s.disponible,
                   "reservado": s.reservado, "promesado": s.promesado, "escriturado": s.escriturado} for s in stock],
        "evolucionMensual": [{"mes": e.mes, "ofertas": e.ofertas, "promesas": e.promesas, "escrituras": e.escrituras}
                              for e in db.query(models.EvolucionMensual).filter_by(upload_id=up.id).all()],
        "canal": [{"canal": c.canal, "reservas": c.reservas, "promesas": c.promesas,
                   "escrituras": c.escrituras, "desistidos": c.desistidos}
                  for c in db.query(models.Canal).filter_by(upload_id=up.id).all()],
        "marketing": {
            "medios": [{"medio": m.medio, "cant": m.cant}
                       for m in db.query(models.MarketingMedio).filter_by(upload_id=up.id).all()],
        },
        "grillaUnidades": [{"torre": g.torre, "piso": g.piso, "depto": g.depto, "estado": g.estado}
                           for g in db.query(models.GrillaUnidad).filter_by(upload_id=up.id).all()],
    }
