from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Literal

# Roles permitidos — exactamente estos strings
RolType = Literal["MESERO", "COCINERO", "ADMIN"]

# --- PARA REGISTRO (INPUT) ---
class UsuarioRegister(BaseModel):
    email: EmailStr
    name: str
    password: str
    rol: RolType = "MESERO"  # Por defecto mesero si no se especifica

    @field_validator("rol")
    @classmethod
    def rol_en_mayusculas(cls, v: str) -> str:
        return v.upper()

# --- PARA LOGIN (INPUT) ---
class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

# --- PARA RESPONDER (OUTPUT) ---
class UsuarioResponse(BaseModel):
    id: int
    email: str
    nombre: str
    rol: str
    fecha_registro: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: UsuarioResponse
