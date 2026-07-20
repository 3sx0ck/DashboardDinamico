from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    nombre: str
    password: str
    rol: str = "visitante"

class UserOut(BaseModel):
    id: int
    email: EmailStr
    nombre: str
    rol: str
    class Config:
        from_attributes = True

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    nombre: str
