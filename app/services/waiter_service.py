import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.data.repositories.waiter_repository import WaiterRepository
from app.domain.schemas.waiter_schemas import WaiterProfileResponse, WaiterProfileUpdate

# Directorio donde se guardan las fotos (relativo a la raíz del proyecto)
PHOTOS_DIR = Path(__file__).resolve().parents[2] / "static" / "photos"
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

MAX_PHOTO_BYTES = 5 * 1024 * 1024  # 5 MB

BASE_URL = os.getenv("BASE_URL", "http://44.212.148.188:8000")


def _build_photo_url(filename: str) -> str:
    return f"{BASE_URL}/static/photos/{filename}"


class WaiterService:

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_profile(self, user_id: int) -> WaiterProfileResponse:
        result = WaiterRepository.get_full(self.db, user_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mesero con id={user_id} no encontrado",
            )
        usuario, profile = result
        return WaiterProfileResponse(
            id=usuario.id,
            name=usuario.nombre,
            phone=profile.phone,
            email=usuario.email,
            photo_url=profile.photo_url,
        )

    def update_profile(self, user_id: int, data: WaiterProfileUpdate) -> WaiterProfileResponse:
        result = WaiterRepository.update_name_phone(
            self.db, user_id, data.name, data.phone
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mesero con id={user_id} no encontrado",
            )
        usuario, profile = result
        return WaiterProfileResponse(
            id=usuario.id,
            name=usuario.nombre,
            phone=profile.phone,
            email=usuario.email,
            photo_url=profile.photo_url,
        )

    async def upload_photo(self, user_id: int, photo: UploadFile) -> str:
        """
        Guarda la imagen en disco y actualiza la URL en la BD.
        Retorna la URL pública de la foto.
        """
        # Verificar que el mesero existe
        result = WaiterRepository.get_full(self.db, user_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mesero con id={user_id} no encontrado",
            )

        # Validar tamaño (leemos en memoria para validar)
        contents = await photo.read()
        if len(contents) > MAX_PHOTO_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La foto supera el límite de 5 MB",
            )

        # Validar tipo MIME básico
        content_type = photo.content_type or ""
        if not content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se aceptan archivos de imagen (JPEG, PNG, etc.)",
            )

        # Nombre único para evitar colisiones
        ext = Path(photo.filename or "photo.jpg").suffix or ".jpg"
        filename = f"waiter_{user_id}_{uuid.uuid4().hex}{ext}"
        file_path = PHOTOS_DIR / filename

        # Guardar en disco
        with open(file_path, "wb") as f:
            f.write(contents)

        # Construir URL pública
        photo_url = _build_photo_url(filename)

        # Persistir en BD
        WaiterRepository.update_photo(self.db, user_id, photo_url)

        return photo_url
