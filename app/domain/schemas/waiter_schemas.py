from pydantic import BaseModel
from typing import Optional


# ── INPUT ──────────────────────────────────────────────────────────────────────

class WaiterProfileUpdate(BaseModel):
    name:  Optional[str] = None
    phone: Optional[str] = None


# ── OUTPUT ─────────────────────────────────────────────────────────────────────

class WaiterProfileResponse(BaseModel):
    """
    Perfil completo del mesero.
    photo_url es una URL pública que Coil carga directamente en la app.
    """
    id:        int
    name:      str
    phone:     Optional[str]
    email:     str
    photo_url: Optional[str]

    class Config:
        from_attributes = True


class PhotoUploadResponse(BaseModel):
    photo_url: str
