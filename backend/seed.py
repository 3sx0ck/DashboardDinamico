from app.db import SessionLocal
from app import models
from app.auth.security import hash_password
from app.config import settings

def run():
    db = SessionLocal()
    if not db.query(models.User).filter_by(email=settings.admin_email).first():
        db.add(models.User(email=settings.admin_email, nombre="Admin",
                            password_hash=hash_password(settings.admin_password), rol="admin"))
        db.commit()
        print("admin creado")
    else:
        print("admin ya existe")
    db.close()

if __name__ == "__main__":
    run()
