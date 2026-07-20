from sqlalchemy.orm import Session
from app import models


def persist_parsed(db: Session, upload: models.Upload, data: dict):
    p = upload.periodo
    uid = upload.id

    # Funnel
    f = data["funnel"]
    db.add(models.Funnel(
        upload_id=uid, periodo=p,
        ofertas=int(f["ofertas"]), desistidos=int(f["desistidos"]),
        en_curso=int(f["enCurso"]), promesas=int(f["promesas"]),
        escrituras=int(f["escrituras"])
    ))

    # Canal
    for c in data["canal"]:
        db.add(models.Canal(
            upload_id=uid, periodo=p,
            canal=c["canal"],
            reservas=int(c["reservas"]),
            promesas=int(c["promesas"]),
            escrituras=int(c["escrituras"]),
            desistidos=int(c["desistidos"])
        ))

    # Evolución Mensual (only fields that exist in model)
    for e in data["evolucionMensual"]:
        db.add(models.EvolucionMensual(
            upload_id=uid, periodo=p,
            mes=e["mes"],
            ofertas=int(e["ofertas"]),
            promesas=int(e["promesas"]),
            escrituras=int(e["escrituras"])
        ))

    # Ventas por torre
    for t in data["ventas"]["porTorre"]:
        db.add(models.Venta(
            upload_id=uid, periodo=p,
            torre=int(t["torre"]),
            venta_uf=float(t["ventaUF"]),
            x_recibir_uf=float(t["xRecibirUF"]),
            escriturados=int(t.get("escriturados", 0))
        ))

    # Stock por torre
    for s in data["stock"]["porTorre"]:
        db.add(models.Stock(
            upload_id=uid, periodo=p,
            torre=int(s["torre"]),
            tipologia=s["tipologia"],
            disponible=int(s.get("disponible", 0)),
            reservado=int(s.get("reservado", 0)),
            promesado=int(s.get("promesado", 0)),
            escriturado=int(s.get("escriturado", 0)),
            bloqueado=int(s.get("bloqueado", 0))
        ))

    # Marketing
    m = data["marketing"]
    for md in m["medios"]:
        db.add(models.MarketingMedio(
            upload_id=uid, periodo=p,
            medio=md["medio"],
            cant=int(md["cant"])
        ))

    for b in m.get("banco", []):
        db.add(models.MarketingBanco(
            upload_id=uid, periodo=p,
            banco=b["banco"],
            pct=float(b["pct"])
        ))

    db.add(models.MarketingKpis(
        upload_id=uid, periodo=p,
        visitas_sala=int(m["visitasSala"]),
        leads_efectivos=int(m["leadsEfectivos"])
    ))

    # Avance Semanal
    a = data["avanceSemanal"]
    db.add(models.AvanceSemanal(
        upload_id=uid, periodo=p,
        semana=(a["semana"] or ""),
        por_firmar=int(a["porFirmar"]),
        firmadas=int(a.get("firmadas", 0))
    ))

    # Grilla de Unidades
    for g in data["grillaUnidades"]:
        db.add(models.GrillaUnidad(
            upload_id=uid, periodo=p,
            torre=int(g["torre"]),
            cara=str(g.get("cara", "")),
            piso=int(g["piso"]),
            depto=str(g["depto"]),
            estado=g["estado"]
        ))

    db.commit()
