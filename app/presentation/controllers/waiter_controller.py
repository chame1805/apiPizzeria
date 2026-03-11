"""
Controller del perfil del mesero.

    GET   /waiters/{id}/profile/   → obtener perfil
    PATCH /waiters/{id}/profile/   → actualizar nombre / teléfono
    POST  /waiters/{id}/photo/     → subir foto de perfil (multipart/form-data)
"""
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.data.sources.database import get_db
from app.domain.schemas.waiter_schemas import (
    PhotoUploadResponse,
    WaiterProfileResponse,
    WaiterProfileUpdate,
)
from app.services.waiter_service import WaiterService

router = APIRouter(prefix="/waiters", tags=["Perfil del mesero"])


@router.get(
    "/{user_id}/profile/",
    response_model=WaiterProfileResponse,
    summary="Obtener perfil del mesero",
)
def get_waiter_profile(
    user_id: int,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_user_id),
):
    """
    Retorna id, name, phone, email y photo_url.
    La app carga photo_url con Coil directamente desde la URL pública.
    """
    service = WaiterService(db)
    return service.get_profile(user_id)


@router.patch(
    "/{user_id}/profile/",
    response_model=WaiterProfileResponse,
    summary="Actualizar nombre y/o teléfono del mesero",
)
def update_waiter_profile(
    user_id: int,
    data: WaiterProfileUpdate,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_user_id),
):
    """
    Actualiza name y/o phone (ambos son opcionales).
    Retorna el perfil completo actualizado.
    """
    service = WaiterService(db)
    return service.update_profile(user_id, data)


@router.post(
    "/{user_id}/photo/",
    response_model=PhotoUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subir foto de perfil del mesero",
)
async def upload_waiter_photo(
    user_id: int,
    photo: UploadFile = File(..., description="Imagen JPEG capturada con la cámara (máx 5 MB)"),
    db: Session = Depends(get_db),
    _: int = Depends(get_current_user_id),
):
    """
    Recibe una imagen en multipart/form-data, campo **photo**.
    - Tamaño máximo: 5 MB.
    - La guarda en /static/photos/ y actualiza photo_url en BD.
    - Retorna { "photo_url": "<url pública y persistente>" }.

    La app guarda localmente esta URL y la usa con Coil en el perfil.
    """
    service = WaiterService(db)
    photo_url = await service.upload_photo(user_id, photo)
    return PhotoUploadResponse(photo_url=photo_url)
