from pydantic import BaseModel
from typing import List

# --- PARA MOSTRAR EL MENÚ ---
class ProductoResponse(BaseModel):
    id: int
    nombre: str
    precio: float

    class Config:
        from_attributes = True

# --- PARA RECIBIR UNA VENTA (INPUT) ---

class ClienteCreate(BaseModel):
    nombre: str
    telefono: str
    direccion: str

class DetallePedido(BaseModel):
    producto_id: int
    cantidad: int

class VentaCreate(BaseModel):
    cliente: ClienteCreate
    items: List[DetallePedido]
    pago_cliente: float

# --- PARA RESPONDER EL TICKET (OUTPUT) ---

class VentaResponse(BaseModel):
    folio: int
    cliente: str
    fecha: str
    total: float
    pago: float
    cambio: float
    mensaje: str