from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.data.sources.database import get_db
from app.domain.schemas.schemas import VentaCreate, VentaResponse
from app.domain.schemas.venta_schemas import OrdenResponse
from app.services.venta_service import VentaService

router = APIRouter(
    prefix="/ordenes",
    tags=["Órdenes"]
)

@router.post("/vender", response_model=VentaResponse, summary="Registrar una nueva venta")
def crear_venta(venta: VentaCreate, db: Session = Depends(get_db)):
    """
    Registra una nueva venta en el sistema.
    """
    servicio = VentaService(db)
    return servicio.registrar_venta(venta)

@router.get("/historial", response_model=List[OrdenResponse], summary="Obtener historial de órdenes")
def obtener_historial(db: Session = Depends(get_db)):
    """
    Obtiene el historial completo de todas las órdenes registradas.
    """
    servicio = VentaService(db)
    return servicio.obtener_historial()

@router.get("/{orden_id}", response_model=OrdenResponse, summary="Obtener una orden específica")
def obtener_orden(orden_id: int, db: Session = Depends(get_db)):
    """
    Obtiene los detalles de una orden específica por su ID.
    """
    servicio = VentaService(db)
    return servicio.obtener_orden_por_id(orden_id)

@router.delete("/{orden_id}", status_code=status.HTTP_200_OK, summary="Eliminar una orden")
def eliminar_orden(orden_id: int, db: Session = Depends(get_db)):
    """
    Elimina una orden del historial.
    """
    servicio = VentaService(db)
    return servicio.eliminar_orden(orden_id)