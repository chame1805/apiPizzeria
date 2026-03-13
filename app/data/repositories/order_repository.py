from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.models.order_models import PizzaOrder


class OrderRepository:

    @staticmethod
    def create(db: Session, data: dict) -> PizzaOrder:
        """Inserta una nueva orden y la retorna con su id y timestamps."""
        order = PizzaOrder(**data)
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def get_active(db: Session) -> List[PizzaOrder]:
        """
        Órdenes activas (PENDING o IN_PROGRESS).
        Optimizado: índice sobre (status, waiter_id) cubre este filtro.
        """
        return (
            db.query(PizzaOrder)
            .filter(PizzaOrder.status.in_(["PENDING", "IN_PROGRESS"]))
            .order_by(PizzaOrder.created_at.asc())
            .all()
        )

    @staticmethod
    def get_by_waiter(db: Session, waiter_id: int) -> List[PizzaOrder]:
        """Órdenes de un mesero con su estado actual real."""
        return (
            db.query(PizzaOrder)
            .filter(PizzaOrder.waiter_id == waiter_id)
            .order_by(PizzaOrder.created_at.desc())
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, order_id: int) -> Optional[PizzaOrder]:
        return db.query(PizzaOrder).filter(PizzaOrder.id == order_id).first()

    @staticmethod
    def update_status(db: Session, order_id: int, new_status: str) -> Optional[PizzaOrder]:
        """Actualiza el estado y el updated_at de la orden."""
        order = db.query(PizzaOrder).filter(PizzaOrder.id == order_id).first()
        if not order:
            return None
        order.status = new_status
        order.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def get_completed_by_waiter(db: Session, waiter_id: int) -> List[PizzaOrder]:
        """
        Órdenes completadas de un mesero específico.
        Optimizado: usa el índice compuesto (status, waiter_id).
        """
        return (
            db.query(PizzaOrder)
            .filter(
                PizzaOrder.waiter_id == waiter_id,
                PizzaOrder.status == "COMPLETED",
            )
            .order_by(PizzaOrder.updated_at.desc())
            .all()
        )
