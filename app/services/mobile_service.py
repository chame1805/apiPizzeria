import os
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.firebase import send_push_to_token
from app.data.repositories.mobile_repository import MobileRepository
from app.domain.models.mobile_models import DevicePushToken, MotionEvent, UserLocation


class MobileService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def register_push_token(self, user_id: int, token: str, platform: str) -> DevicePushToken:
        return MobileRepository.upsert_push_token(
            db=self.db,
            user_id=user_id,
            token=token,
            platform=platform,
        )

    def unregister_push_token(self, user_id: int, token: str) -> bool:
        deleted = MobileRepository.delete_push_token(
            db=self.db,
            user_id=user_id,
            token=token,
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token no encontrado para el usuario autenticado",
            )
        return True

    def save_location(
        self,
        user_id: int,
        latitude: float,
        longitude: float,
        accuracy_meters: Optional[float],
        speed_mps: Optional[float],
        heading_degrees: Optional[float],
        altitude_meters: Optional[float],
        captured_at,
    ) -> UserLocation:
        return MobileRepository.create_location(
            db=self.db,
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            accuracy_meters=accuracy_meters,
            speed_mps=speed_mps,
            heading_degrees=heading_degrees,
            altitude_meters=altitude_meters,
            captured_at=captured_at,
        )

    def get_latest_location(self, user_id: int) -> UserLocation:
        row = MobileRepository.get_latest_location(self.db, user_id=user_id)
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay ubicación registrada para este usuario",
            )
        return row

    def save_motion_event(
        self,
        user_id: int,
        axis_x: float,
        axis_y: float,
        axis_z: float,
        magnitude: float,
        is_significant: bool,
        source: str,
        captured_at,
    ) -> MotionEvent:
        return MobileRepository.create_motion_event(
            db=self.db,
            user_id=user_id,
            axis_x=axis_x,
            axis_y=axis_y,
            axis_z=axis_z,
            magnitude=magnitude,
            is_significant=is_significant,
            source=source,
            captured_at=captured_at,
        )

    def get_latest_motion_event(self, user_id: int) -> MotionEvent:
        row = MobileRepository.get_latest_motion_event(self.db, user_id=user_id)
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay eventos de movimiento registrados para este usuario",
            )
        return row

    @staticmethod
    def is_firebase_enabled() -> bool:
        return bool(os.getenv("FIREBASE_PROJECT_ID"))

    def notify_order_completed(self, user_id: int, order_id: int, pizza_name: str, table_number: int) -> int:
        tokens = MobileRepository.get_active_push_tokens_for_user(self.db, user_id=user_id)
        sent = 0
        for token_row in tokens:
            send_push_to_token(
                token=token_row.token,
                title="Orden lista",
                body=f"{pizza_name} de mesa {table_number} está COMPLETED",
                data={
                    "event": "ORDER_COMPLETED",
                    "order_id": str(order_id),
                    "pizza_name": pizza_name,
                    "table_number": str(table_number),
                    "status": "COMPLETED",
                },
            )
            sent += 1
        return sent
