from pydantic import BaseModel
from typing import List

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