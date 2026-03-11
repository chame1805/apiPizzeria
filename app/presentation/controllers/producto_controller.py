from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.data.sources.database import get_db
from app.services.producto_service import ProductoService
from app.domain.schemas.producto_schemas import ProductoResponse, ProductoCreate, ProductoUpdate
from app.core.security import get_current_user_id, require_rol

router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)

# Lectura: cualquier usuario autenticado puede ver el menú
@router.get("/", response_model=List[ProductoResponse], summary="Listar todos los productos")
def listar_productos(db: Session = Depends(get_db)):
    """
    Obtiene el listado completo de productos (pizzas) disponibles.
    No requiere autenticación (es el menú público).
    """
    productos = ProductoService.listar_productos(db)
    return productos

@router.get("/{producto_id}", response_model=ProductoResponse, summary="Obtener un producto por ID")
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = ProductoService.obtener_producto(db, producto_id)
    return producto

# Escritura: solo ADMIN
@router.post(
    "/",
    response_model=ProductoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo producto (solo ADMIN)",
    dependencies=[Depends(require_rol("ADMIN"))],
)
def crear_producto(datos: ProductoCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo producto (pizza) en el sistema.
    **Requiere rol ADMIN.**
    """
    producto = ProductoService.crear_producto(db, datos)
    return producto

@router.put(
    "/{producto_id}",
    response_model=ProductoResponse,
    summary="Actualizar un producto (solo ADMIN)",
    dependencies=[Depends(require_rol("ADMIN"))],
)
def actualizar_producto(producto_id: int, datos: ProductoUpdate, db: Session = Depends(get_db)):
    """
    Actualiza la información de un producto existente.
    **Requiere rol ADMIN.**
    """
    producto = ProductoService.actualizar_producto(db, producto_id, datos)
    return producto

@router.delete(
    "/{producto_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar un producto (solo ADMIN)",
    dependencies=[Depends(require_rol("ADMIN"))],
)
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    """
    Elimina un producto del sistema.
    **Requiere rol ADMIN.**
    """
    resultado = ProductoService.eliminar_producto(db, producto_id)
    return resultado
