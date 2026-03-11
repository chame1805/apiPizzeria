from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.data.sources.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class PizzaOrder(Base):
    """
    Orden de pizza generada por el mesero.
    Estados posibles (deben coincidir con el enum Kotlin):
        PENDING      → recién creada, esperando cocina
        IN_PROGRESS  → la cocina la está preparando
        COMPLETED    → lista para que el mesero la recoja
    """
    __tablename__ = "pizza_orders"

    id              = Column(Integer, primary_key=True, index=True)
    pizza_name      = Column(String(100), nullable=False)
    price           = Column(Numeric(10, 2), nullable=False)
    client_name     = Column(String(100), nullable=False)
    total_paid      = Column(Numeric(10, 2), nullable=False)
    change_returned = Column(Numeric(10, 2), nullable=False)
    waiter_id       = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    table_number    = Column(Integer, nullable=False)
    status          = Column(String(20), nullable=False, default="PENDING", index=True)
    created_at      = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at      = Column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)

    # Índice compuesto para la consulta más frecuente: status + waiter_id
    __table_args__ = (
        Index("ix_pizza_orders_status_waiter", "status", "waiter_id"),
    )


class WaiterProfile(Base):
    """
    Perfil extendido del mesero (1-a-1 con Usuario).
    Contiene campos que no están en la tabla usuarios base.
    """
    __tablename__ = "waiter_profiles"

    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False, index=True)
    phone     = Column(String(30), nullable=True)
    photo_url = Column(String(500), nullable=True)

    usuario = relationship("Usuario", foreign_keys=[user_id])
