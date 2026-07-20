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
    up = models.Upload(periodo=periodo, filename=file.filename, bucket_key=key, uploaded_by=admin.id)
    db.add(up)
    db.commit()
    db.refresh(up)
    persist_parsed(db, up, data)

    return {"upload_id": up.id, "periodo": periodo}
