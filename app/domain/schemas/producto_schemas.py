from pydantic import BaseModel, Field
from typing import Optional

class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del producto")
    precio: float = Field(..., gt=0, description="Precio del producto")

class ProductoCreate(ProductoBase):
    """Schema para crear un producto"""
    pass

class ProductoUpdate(BaseModel):
    """Schema para actualizar un producto (campos opcionales)"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    precio: Optional[float] = Field(None, gt=0)

class ProductoResponse(BaseModel):
    """Schema para responder con datos del producto"""
    id: int
    nombre: str
    precio: float

    class Config:
        from_attributes = True
