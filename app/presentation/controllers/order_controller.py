"""
Controller de órdenes de pizza.

Endpoints REST:
    POST   /orders/                        → crear orden (mesero)
    PATCH  /orders/{id}/status/            → cambiar estado (cocina)
    GET    /orders/{waiter_id}/completed/  → fallback polling mesero (por si el WS cae)

WebSocket:
    WS  /orders/ws/kitchen                 → cocina recibe push de órdenes nuevas y cambios
    WS  /orders/ws/waiter/{waiter_id}      → mesero recibe push cuando su orden está COMPLETED
"""
from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.security import get_current_user_id, decode_token_ws
from app.core.security import decode_token_ws_payload
from app.core.websocket_manager import kitchen_manager, waiter_manager
from app.data.sources.database import get_db
from app.domain.schemas.order_schemas import (
    OrderCreate,
    OrderCompletedItem,
    OrderKitchenItem,
    OrderResponse,
    OrderStatusResponse,
    OrderStatusUpdate,
    OrderWaiterItem,
)
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Órdenes (cocina/mesero)"])


# ── WebSocket ──────────────────────────────────────────────────────────────────

@router.websocket("/ws/kitchen")
async def kitchen_websocket(
    websocket: WebSocket,
    token: Optional[str] = None,
):
    """
    Conexión WebSocket para la pantalla de cocina.

    La cocina se conecta UNA sola vez y queda suscrita.
    El servidor hace broadcast automático cuando:
        • llega una orden nueva (POST /orders/)
        • una orden cambia de estado (PATCH /orders/{id}/status/)

    Autenticación: pasar ?token=<jwt_bearer> como query param.
    Si el token es inválido se cierra la conexión con código 1008.
    """
    if token is None or decode_token_ws(token) is None:
        await websocket.close(code=1008)
        return

    await kitchen_manager.connect(websocket)
    try:
        # Mantener la conexión viva; el cliente puede mandar pings de texto.
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        kitchen_manager.disconnect(websocket)


@router.websocket("/ws/waiter/{waiter_id}")
async def waiter_websocket(
    websocket: WebSocket,
    waiter_id: int,
    token: Optional[str] = None,
):
    """
    Conexión WebSocket para el mesero.

    El mesero se conecta al abrir la app con su waiter_id.
    El servidor le envía un mensaje push cuando la cocina marca
    alguna de sus órdenes como COMPLETED → la app vibra al recibir
    el evento sin necesidad de polling.

    Autenticación: pasar ?token=<jwt_bearer> como query param.
    Si el token es inválido se cierra la conexión con código 1008.

    Mensaje que recibe el mesero:
        {
            "event":        "ORDER_COMPLETED",
            "id":           5,
            "pizza_name":   "Pepperoni",
            "table_number": 3,
            "status":       "COMPLETED",
            "updated_at":   "2026-03-10T15:30:00Z"
        }
    """
    if token is None:
        await websocket.close(code=1008)
        return

    payload = decode_token_ws_payload(token)
    if payload is None:
        await websocket.close(code=1008)
        return

    token_user_id = payload.get("id")
    if token_user_id is None or int(token_user_id) != waiter_id:
        await websocket.close(code=1008)
        return

    await waiter_manager.connect(websocket, waiter_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        waiter_manager.disconnect(websocket, waiter_id)


# ── REST ───────────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva orden (mesero)",
)
async def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_user_id),
):
    """
    El mesero manda la orden desde su celular.
    - El estado inicial siempre es **PENDING**.
    - Tras crear la orden, hace broadcast WebSocket a todas las
      pantallas de cocina conectadas.
    """
    service = OrderService(db)
    order = service.create_order(data)

    # Serializar para broadcast (fechas a ISO 8601 UTC)
    payload = {
        "event":        "NEW_ORDER",
        "id":           order.id,
        "pizza_name":   order.pizza_name,
        "table_number": order.table_number,
        "client_name":  order.client_name,
        "status":       order.status,
        "created_at":   order.created_at.isoformat(),
    }
    await kitchen_manager.broadcast(payload)

    return order


@router.get(
    "/",
    response_model=List[OrderWaiterItem],
    summary="Órdenes del mesero autenticado con estado actual real",
)
def get_waiter_orders(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Devuelve las órdenes del mesero autenticado con su estado actual real.
    """
    service = OrderService(db)
    return service.get_orders_for_waiter(current_user_id)


@router.get(
    "/kitchen/active/",
    response_model=List[OrderKitchenItem],
    summary="Órdenes activas para cocina (PENDING | IN_PROGRESS)",
)
def get_active_orders_for_kitchen(
    db: Session = Depends(get_db),
    _: int = Depends(get_current_user_id),
):
    """
    Devuelve las órdenes que todavía no están COMPLETED/DELIVERED.
    """
    service = OrderService(db)
    return service.get_active_orders()


@router.patch(
    "/{order_id}/status/",
    response_model=OrderStatusResponse,
    summary="Cambiar estado de una orden (cocina)",
)
async def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_user_id),
):
    """
    La cocina usa este endpoint para mover la orden de
    PENDING → IN_PROGRESS → COMPLETED.

    Tras actualizar, hace broadcast WebSocket a todas las pantallas
    de cocina conectadas.
    """
    service = OrderService(db)
    order = service.update_order_status(order_id, data.status)

    kitchen_payload = {
        "event":      "ORDER_STATUS_CHANGED",
        "id":         order.id,
        "order_id":   order.id,
        "status":     order.status,
        "new_status": order.status,
        "order_status": order.status,
        "updated_at": order.updated_at.isoformat(),
    }
    await kitchen_manager.broadcast(kitchen_payload)

    waiter_status_payload = {
        "event":      "ORDER_STATUS_CHANGED",
        "id":         order.id,
        "order_id":   order.id,
        "status":     order.status,
        "new_status": order.status,
        "order_status": order.status,
        "pizza_name": order.pizza_name,
        "table_number": order.table_number,
        "updated_at": order.updated_at.isoformat(),
    }
    await waiter_manager.send_to_waiter(order.waiter_id, waiter_status_payload)

    # Si la orden quedó COMPLETED, avisar directamente al mesero por WS
    if order.status == "COMPLETED":
        waiter_payload = {
            "event":        "ORDER_COMPLETED",
            "id":           order.id,
            "order_id":     order.id,
            "pizza_name":   order.pizza_name,
            "price":        float(order.price),
            "total_paid":   float(order.total_paid),
            "change_returned": float(order.change_returned),
            "table_number": order.table_number,
            "status":       order.status,
            "new_status":   order.status,
            "order_status": order.status,
            "updated_at":   order.updated_at.isoformat(),
        }
        await waiter_manager.send_to_waiter(order.waiter_id, waiter_payload)

    return order


@router.get(
    "/{waiter_id}/completed/",
    response_model=List[OrderCompletedItem],
    summary="Órdenes completadas del mesero (fallback / historial)",
)
def get_completed_orders(
    waiter_id: int,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_user_id),
):
    """
    Retorna todas las órdenes COMPLETED del mesero.

    Uso recomendado: llamarlo UNA sola vez al iniciar la app para cargar
    el historial, y luego confiar en el WebSocket /ws/waiter/{waiter_id}
    para recibir nuevas notificaciones en tiempo real.
    También sirve de fallback si el WebSocket se desconecta.
    """
    service = OrderService(db)
    return service.get_completed_orders_for_waiter(waiter_id)
