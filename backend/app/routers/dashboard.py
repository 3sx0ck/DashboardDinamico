from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app import models
from app.auth.deps import current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _latest_periodo(db):
    row = db.query(models.Upload).order_by(models.Upload.created_at.desc()).first()
    return row.periodo if row else None


@router.get("")
def dashboard(periodo: Optional[str] = None, torre: Optional[int] = None,
              db: Session = Depends(get_db), _: models.User = Depends(current_user)):
    p = periodo or _latest_periodo(db)
    if not p:
        return {"periodo": None, "empty": True}

    def q(M):
        query = db.query(M).filter(M.periodo == p)
        if torre and hasattr(M, "torre"):
            query = query.filter(M.torre == torre)
        return query.all()

    funnel = db.query(models.Funnel).filter_by(periodo=p).first()
    ventas = q(models.Venta)
    stock = q(models.Stock)

    return {
        "periodo": p,
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
                              for e in db.query(models.EvolucionMensual).filter_by(periodo=p).all()],
        "canal": [{"canal": c.canal, "reservas": c.reservas, "promesas": c.promesas,
                   "escrituras": c.escrituras, "desistidos": c.desistidos}
                  for c in db.query(models.Canal).filter_by(periodo=p).all()],
        "marketing": {
            "medios": [{"medio": m.medio, "cant": m.cant}
                       for m in db.query(models.MarketingMedio).filter_by(periodo=p).all()],
        },
        "grillaUnidades": [{"torre": g.torre, "piso": g.piso, "depto": g.depto, "estado": g.estado}
                           for g in db.query(models.GrillaUnidad).filter_by(periodo=p).all()],
    }
