from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from app.config import settings

pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(p: str) -> str:
    return pwd.hash(p)

def verify_password(p: str, h: str) -> bool:
    return pwd.verify(p, h)

def create_token(claims: dict) -> str:
    to_encode = claims.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
