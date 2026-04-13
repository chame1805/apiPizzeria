from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.models.mobile_models import DevicePushToken, MotionEvent, UserLocation


class MobileRepository:
    @staticmethod
    def upsert_push_token(db: Session, user_id: int, token: str, platform: str) -> DevicePushToken:
        existing = (
            db.query(DevicePushToken)
            .filter(DevicePushToken.token == token)
            .first()
        )
        if existing:
            existing.user_id = user_id
            existing.platform = platform
            existing.is_active = True
            existing.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            return existing

        row = DevicePushToken(
            user_id=user_id,
            token=token,
            platform=platform,
            is_active=True,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def delete_push_token(db: Session, user_id: int, token: str) -> bool:
        row = (
            db.query(DevicePushToken)
            .filter(
                DevicePushToken.user_id == user_id,
                DevicePushToken.token == token,
            )
            .first()
        )
        if not row:
            return False
        db.delete(row)
        db.commit()
        return True

    @staticmethod
    def get_active_push_tokens_for_user(db: Session, user_id: int) -> List[DevicePushToken]:
        return (
            db.query(DevicePushToken)
            .filter(
                DevicePushToken.user_id == user_id,
                DevicePushToken.is_active.is_(True),
            )
            .all()
        )

    @staticmethod
    def create_location(
        db: Session,
        user_id: int,
        latitude: float,
        longitude: float,
        accuracy_meters: Optional[float],
        speed_mps: Optional[float],
        heading_degrees: Optional[float],
        altitude_meters: Optional[float],
        captured_at: Optional[datetime],
    ) -> UserLocation:
        row = UserLocation(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            accuracy_meters=accuracy_meters,
            speed_mps=speed_mps,
            heading_degrees=heading_degrees,
            altitude_meters=altitude_meters,
            captured_at=captured_at or datetime.now(timezone.utc),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def get_latest_location(db: Session, user_id: int) -> Optional[UserLocation]:
        return (
            db.query(UserLocation)
            .filter(UserLocation.user_id == user_id)
            .order_by(UserLocation.captured_at.desc())
            .first()
        )

    @staticmethod
    def create_motion_event(
        db: Session,
        user_id: int,
        axis_x: float,
        axis_y: float,
        axis_z: float,
        magnitude: float,
        is_significant: bool,
        source: str,
        captured_at: Optional[datetime],
    ) -> MotionEvent:
        row = MotionEvent(
            user_id=user_id,
            axis_x=axis_x,
            axis_y=axis_y,
            axis_z=axis_z,
            magnitude=magnitude,
            is_significant=is_significant,
            source=source,
            captured_at=captured_at or datetime.now(timezone.utc),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def get_latest_motion_event(db: Session, user_id: int) -> Optional[MotionEvent]:
        return (
            db.query(MotionEvent)
            .filter(MotionEvent.user_id == user_id)
            .order_by(MotionEvent.captured_at.desc())
            .first()
        )
