from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.data.sources.database import get_db
from app.domain.schemas.mobile_schemas import (
    LocationCreateRequest,
    LocationResponse,
    MotionEventCreateRequest,
    MotionEventResponse,
    PushTokenDeleteResponse,
    PushTokenResponse,
    PushTokenUpsertRequest,
)
from app.services.mobile_service import MobileService

router = APIRouter(prefix="/mobile", tags=["Mobile integration"])


@router.post(
    "/push-tokens/",
    response_model=PushTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar o actualizar token FCM del dispositivo",
)
def register_push_token(
    data: PushTokenUpsertRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    service = MobileService(db)
    return service.register_push_token(
        user_id=current_user_id,
        token=data.token,
        platform=data.platform,
    )


@router.delete(
    "/push-tokens/",
    response_model=PushTokenDeleteResponse,
    summary="Eliminar token FCM del usuario autenticado",
)
def unregister_push_token(
    token: str = Query(..., min_length=20, max_length=300),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    service = MobileService(db)
    service.unregister_push_token(user_id=current_user_id, token=token)
    return PushTokenDeleteResponse(deleted=True, token=token)


@router.post(
    "/location/",
    response_model=LocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Guardar lectura GPS del usuario autenticado",
)
def create_location(
    data: LocationCreateRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    service = MobileService(db)
    return service.save_location(
        user_id=current_user_id,
        latitude=data.latitude,
        longitude=data.longitude,
        accuracy_meters=data.accuracy_meters,
        speed_mps=data.speed_mps,
        heading_degrees=data.heading_degrees,
        altitude_meters=data.altitude_meters,
        captured_at=data.captured_at,
    )


@router.get(
    "/location/latest/",
    response_model=LocationResponse,
    summary="Obtener última ubicación GPS del usuario autenticado",
)
def get_latest_location(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    service = MobileService(db)
    return service.get_latest_location(user_id=current_user_id)


@router.post(
    "/motion-events/",
    response_model=MotionEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Guardar evento de acelerómetro del usuario autenticado",
)
def create_motion_event(
    data: MotionEventCreateRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    service = MobileService(db)
    return service.save_motion_event(
        user_id=current_user_id,
        axis_x=data.axis_x,
        axis_y=data.axis_y,
        axis_z=data.axis_z,
        magnitude=data.magnitude,
        is_significant=data.is_significant,
        source=data.source,
        captured_at=data.captured_at,
    )


@router.get(
    "/motion-events/latest/",
    response_model=MotionEventResponse,
    summary="Obtener último evento de acelerómetro del usuario autenticado",
)
def get_latest_motion_event(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    service = MobileService(db)
    return service.get_latest_motion_event(user_id=current_user_id)
