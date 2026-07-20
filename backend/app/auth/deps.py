from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db import get_db
from app.auth.security import decode_token
from app import models

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)) -> models.User:
    try:
        data = decode_token(token)
        user = db.get(models.User, int(data["sub"]))
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "token inválido")
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "usuario no existe")
    return user

def require_admin(user: models.User = Depends(current_user)) -> models.User:
    if user.rol != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "requiere admin")
    return user
