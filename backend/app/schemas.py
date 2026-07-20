from pydantic import BaseModel

# str (no EmailStr): email-validator rechaza dominios como .local/.internal
# como "reserved TLD" (el admin sembrado usa admin@pmk.local), y eso
# crasheaba GET /api/users con 500 al serializar la respuesta. Herramienta
# interna, no necesita validación estricta de email.
class UserCreate(BaseModel):
    email: str
    nombre: str
    password: str
    rol: str = "visitante"

class UserOut(BaseModel):
    id: int
    email: str
    nombre: str
    rol: str
    class Config:
        from_attributes = True

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    nombre: str
