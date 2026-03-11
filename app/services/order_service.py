from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.data.repositories.order_repository import OrderRepository
from app.domain.models.order_models import PizzaOrder
from app.domain.schemas.order_schemas import OrderCreate, OrderStatus


class OrderService:

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_order(self, data: OrderCreate) -> PizzaOrder:
        """Crea una orden nueva con estado PENDING."""
        order_dict = {
            "pizza_name":      data.pizza_name,
            "price":           data.price,
            "client_name":     data.client_name,
            "total_paid":      data.total_paid,
            "change_returned": data.change_returned,
            "waiter_id":       data.waiter_id,
            "table_number":    data.table_number,
            "status":          data.status.value,
        }
        return OrderRepository.create(self.db, order_dict)

    def get_active_orders(self) -> List[PizzaOrder]:
        """Retorna órdenes PENDING e IN_PROGRESS para la cocina."""
        return OrderRepository.get_active(self.db)

    def update_order_status(self, order_id: int, new_status: OrderStatus) -> PizzaOrder:
        """Cambia el estado de una orden. Lanza 404 si no existe."""
        order = OrderRepository.update_status(self.db, order_id, new_status.value)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden con id={order_id} no encontrada",
            )
        return order

    def get_completed_orders_for_waiter(self, waiter_id: int) -> List[PizzaOrder]:
        """Retorna órdenes COMPLETED del mesero para el polling de notificación."""
        return OrderRepository.get_completed_by_waiter(self.db, waiter_id)
