from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class PushTokenUpsertRequest(BaseModel):
    token: str = Field(min_length=20, max_length=300)
    platform: str = Field(default="ANDROID", min_length=3, max_length=20)

    @field_validator("platform")
    @classmethod
    def normalize_platform(cls, value: str) -> str:
        return value.upper()


class PushTokenResponse(BaseModel):
    id: int
    user_id: int
    token: str
    platform: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PushTokenDeleteResponse(BaseModel):
    deleted: bool
    token: str


class LocationCreateRequest(BaseModel):
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    accuracy_meters: Optional[float] = Field(default=None, ge=0)
    speed_mps: Optional[float] = Field(default=None, ge=0)
    heading_degrees: Optional[float] = Field(default=None, ge=0, le=360)
    altitude_meters: Optional[float] = None
    captured_at: Optional[datetime] = None


class LocationResponse(BaseModel):
    id: int
    user_id: int
    latitude: float
    longitude: float
    accuracy_meters: Optional[float]
    speed_mps: Optional[float]
    heading_degrees: Optional[float]
    altitude_meters: Optional[float]
    captured_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class MotionEventCreateRequest(BaseModel):
    axis_x: float
    axis_y: float
    axis_z: float
    magnitude: float = Field(ge=0)
    is_significant: bool = False
    source: str = Field(default="ACCELEROMETER", min_length=3, max_length=40)
    captured_at: Optional[datetime] = None

    @field_validator("source")
    @classmethod
    def normalize_source(cls, value: str) -> str:
        return value.upper()


class MotionEventResponse(BaseModel):
    id: int
    user_id: int
    axis_x: float
    axis_y: float
    axis_z: float
    magnitude: float
    is_significant: bool
    source: str
    captured_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
