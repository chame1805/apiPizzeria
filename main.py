from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path

# Imports de módulos existentes
from app.data.sources.database import engine, Base, get_db
from app.domain.models.models import Producto
from app.domain.schemas.schemas import ProductoResponse
from app.presentation.controllers import venta_controller, auth_controller, producto_controller

# Importar los nuevos modelos para que Base los registre ANTES de create_all
import app.domain.models.order_models  # noqa: F401 – registra PizzaOrder y WaiterProfile

# Importar los nuevos controllers
from app.presentation.controllers import order_controller, waiter_controller

# Crear / sincronizar tablas automáticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pizzería API",
    description="API para la app móvil de pizzería: auth, productos, órdenes con WebSocket y perfil de mesero.",
    version="2.0.0",
)

# --- ARCHIVOS ESTÁTICOS (fotos de meseros) ---
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
(STATIC_DIR / "photos").mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# --- ROUTERS EXISTENTES ---
app.include_router(venta_controller.router)
app.include_router(auth_controller.router)
app.include_router(producto_controller.router)

# --- ROUTERS NUEVOS ---
app.include_router(order_controller.router)
app.include_router(waiter_controller.router)

# --- ENDPOINT SIMPLE DE MENÚ ---
@app.get("/menu", response_model=List[ProductoResponse])
def obtener_menu(db: Session = Depends(get_db)):
    return db.query(Producto).all()