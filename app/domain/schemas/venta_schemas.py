from pydantic import BaseModel
from typing import List, Optional

class VentaCreate(BaseModel):
    cliente_id: int
    pizzas_ids: List[int]
    dinero_entregado: float

class VentaResponse(BaseModel):
    id_orden: int
    total: float
    cambio: float
    mensaje: str

    class Config:
        from_attributes = True

class DetalleOrdenResponse(BaseModel):
    """Schema para el detalle de una orden"""
    producto_id: int
    producto_nombre: str
    cantidad: int
    precio_unitario: float
    subtotal: float

    class Config:
        from_attributes = True

class OrdenResponse(BaseModel):
    """Schema para responder con datos de una orden completa"""
    id: int
    cliente_nombre: str
    fecha: Optional[str]
    total_venta: float
    pago_cliente: float
    cambio: float
    estatus: str
    detalles: List[DetalleOrdenResponse]

    class Config:
        from_attributes = True