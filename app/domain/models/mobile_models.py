from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)

from app.data.sources.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class DevicePushToken(Base):
    __tablename__ = "device_push_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    token = Column(String(300), nullable=False, unique=True, index=True)
    platform = Column(String(20), nullable=False, default="ANDROID")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)


class UserLocation(Base):
    __tablename__ = "user_locations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy_meters = Column(Float, nullable=True)
    speed_mps = Column(Float, nullable=True)
    heading_degrees = Column(Float, nullable=True)
    altitude_meters = Column(Float, nullable=True)
    captured_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    __table_args__ = (
        Index("ix_user_locations_user_captured", "user_id", "captured_at"),
    )


class MotionEvent(Base):
    __tablename__ = "motion_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    axis_x = Column(Float, nullable=False)
    axis_y = Column(Float, nullable=False)
    axis_z = Column(Float, nullable=False)
    magnitude = Column(Float, nullable=False)
    is_significant = Column(Boolean, nullable=False, default=False)
    source = Column(String(40), nullable=False, default="ACCELEROMETER")
    captured_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    __table_args__ = (
        Index("ix_motion_events_user_captured", "user_id", "captured_at"),
    )
