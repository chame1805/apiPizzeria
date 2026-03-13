from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class OrderStatus(str, Enum):
    """
    Enum que DEBE coincidir carácter a carácter con el enum Kotlin de la app.
    Android hace un valueOf(string), cualquier diferencia rompe la deserialización.
    """
    PENDING     = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED   = "COMPLETED"
    DELIVERED   = "DELIVERED"


# ── INPUT ──────────────────────────────────────────────────────────────────────

class OrderCreate(BaseModel):
    pizza_name:      str
    price:           float
    client_name:     str
    total_paid:      float
    change_returned: float
    waiter_id:       int
    table_number:    int
    status:          OrderStatus = OrderStatus.PENDING


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


# ── OUTPUT ─────────────────────────────────────────────────────────────────────

class OrderResponse(BaseModel):
    """Respuesta completa al crear una orden (POST /orders/)."""
    id:              int
    pizza_name:      str
    price:           float
    client_name:     str
    total_paid:      float
    change_returned: float
    waiter_id:       int
    table_number:    int
    status:          str
    created_at:      datetime
    updated_at:      datetime

    class Config:
        from_attributes = True


class OrderKitchenItem(BaseModel):
    """Item que ve la pantalla de cocina (GET /orders/ y broadcast WS)."""
    id:           int
    pizza_name:   str
    table_number: int
    client_name:  str
    status:       str
    created_at:   datetime

    class Config:
        from_attributes = True


class OrderStatusResponse(BaseModel):
    """Respuesta al cambiar estado (PATCH /orders/{id}/status/)."""
    id:         int
    status:     str
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderCompletedItem(BaseModel):
    """Item que ve la app del mesero en polling (GET /orders/{waiter_id}/completed/)."""
    id:           int
    pizza_name:   str
    price:        float
    total_paid:   float
    change_returned: float
    table_number: int
    status:       str
    updated_at:   datetime

    class Config:
        from_attributes = True


class OrderWaiterItem(BaseModel):
    """Item de orden para la vista principal del mesero (GET /orders/)."""
    id:              int
    pizza_name:      str
    price:           float
    client_name:     str
    total_paid:      float
    change_returned: float
    waiter_id:       int
    table_number:    int
    status:          str
    created_at:      datetime
    updated_at:      datetime

    class Config:
        from_attributes = True
