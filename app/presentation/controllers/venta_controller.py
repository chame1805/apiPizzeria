from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.data.sources.database import get_db
from app.domain.schemas.schemas import VentaCreate, VentaResponse
from app.services.venta_service import VentaService

router = APIRouter()

@router.post("/vender", response_model=VentaResponse)
def crear_venta(venta: VentaCreate, db: Session = Depends(get_db)):
    servicio = VentaService(db)
    return servicio.registrar_venta(venta)