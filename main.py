from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List

# Imports de tus módulos
from app.data.sources.database import engine, Base, get_db
from app.domain.models.models import Producto
from app.domain.schemas.schemas import ProductoResponse
from app.presentation.controllers import venta_controller # Importamos el controlador nuevo

# Crear tablas automáticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pizzería API Clean Arch")

# --- CONECTAR EL ROUTER DE VENTAS ---
app.include_router(venta_controller.router)

# --- ENDPOINT SIMPLE DE MENÚ ---
@app.get("/menu", response_model=List[ProductoResponse])
def obtener_menu(db: Session = Depends(get_db)):
    return db.query(Producto).all()