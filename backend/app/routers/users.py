from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app import models
from app.auth.deps import require_admin
from app.auth.security import hash_password
from app.schemas import UserCreate, UserOut

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    return db.query(models.User).all()

@router.post("", response_model=UserOut, status_code=201)
def create_user(body: UserCreate, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    if body.rol not in ("admin", "visitante"):
        raise HTTPException(400, "rol inválido")
    if db.query(models.User).filter_by(email=body.email).first():
        raise HTTPException(409, "email ya existe")
    u = models.User(email=body.email, nombre=body.nombre,
                    password_hash=hash_password(body.password), rol=body.rol)
    db.add(u); db.commit(); db.refresh(u)
    return u

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), me: models.User = Depends(require_admin)):
    if user_id == me.id:
        raise HTTPException(400, "no puede eliminarse a sí mismo")
    u = db.get(models.User, user_id)
    if not u:
        raise HTTPException(404, "no existe")
    admins = db.query(models.User).filter_by(rol="admin").count()
    if u.rol == "admin" and admins <= 1:
        raise HTTPException(400, "no puede eliminar el último admin")
    db.delete(u); db.commit()
