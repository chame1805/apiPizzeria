from fastapi import WebSocket
from typing import Dict, List


class KitchenConnectionManager:
    """
    Gestiona conexiones WebSocket activas de la pantalla de cocina.
    Broadcast a todos cuando llega orden nueva o cambia de estado.
    """

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict) -> None:
        """Envía un mensaje JSON a todas las conexiones activas de cocina."""
        dead: List[WebSocket] = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for conn in dead:
            self.disconnect(conn)


class WaiterConnectionManager:
    """
    Gestiona conexiones WebSocket de meseros individuales.
    Cada mesero se conecta con su waiter_id y solo recibe eventos
    de sus propias órdenes (ej: cuando la cocina marca COMPLETED).
    """

    def __init__(self) -> None:
        # waiter_id → lista de conexiones activas de ese mesero
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, waiter_id: int) -> None:
        await websocket.accept()
        if waiter_id not in self.active_connections:
            self.active_connections[waiter_id] = []
        self.active_connections[waiter_id].append(websocket)

    def disconnect(self, websocket: WebSocket, waiter_id: int) -> None:
        connections = self.active_connections.get(waiter_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections:
            self.active_connections.pop(waiter_id, None)

    async def send_to_waiter(self, waiter_id: int, message: dict) -> None:
        """Envía un mensaje JSON solo al mesero con ese waiter_id."""
        connections = self.active_connections.get(waiter_id, [])
        dead: List[WebSocket] = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for conn in dead:
            self.disconnect(conn, waiter_id)


# Instancias globales compartidas por controllers y services
kitchen_manager = KitchenConnectionManager()
waiter_manager  = WaiterConnectionManager()
