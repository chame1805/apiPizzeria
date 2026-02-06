from pydantic import BaseModel, EmailStr
from datetime import datetime

# --- PARA REGISTRO (INPUT) ---
class UsuarioRegister(BaseModel):
    email: EmailStr
    name: str
    password: str

# --- PARA LOGIN (INPUT) ---
class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

# --- PARA RESPONDER (OUTPUT) ---
class UsuarioResponse(BaseModel):
    id: int
    email: str
    nombre: str
    fecha_registro: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: UsuarioResponse
