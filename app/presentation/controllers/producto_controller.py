from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.data.sources.database import get_db
from app.services.producto_service import ProductoService
from app.domain.schemas.producto_schemas import ProductoResponse, ProductoCreate, ProductoUpdate

router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)

@router.get("/", response_model=List[ProductoResponse], summary="Listar todos los productos")
def listar_productos(db: Session = Depends(get_db)):
    """
    Obtiene el listado completo de productos (pizzas) disponibles.
    """
    productos = ProductoService.listar_productos(db)
    return productos

@router.get("/{producto_id}", response_model=ProductoResponse, summary="Obtener un producto por ID")
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    """
    Obtiene la información de un producto específico por su ID.
    """
    producto = ProductoService.obtener_producto(db, producto_id)
    return producto

@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo producto")
def crear_producto(datos: ProductoCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo producto (pizza) en el sistema.
    
    - **nombre**: Nombre del producto (debe ser único)
    - **precio**: Precio del producto (debe ser mayor a 0)
    """
    producto = ProductoService.crear_producto(db, datos)
    return producto

@router.put("/{producto_id}", response_model=ProductoResponse, summary="Actualizar un producto")
def actualizar_producto(producto_id: int, datos: ProductoUpdate, db: Session = Depends(get_db)):
    """
    Actualiza la información de un producto existente.
    
    - **nombre**: Nuevo nombre del producto (opcional)
    - **precio**: Nuevo precio del producto (opcional)
    """
    producto = ProductoService.actualizar_producto(db, producto_id, datos)
    return producto

@router.delete("/{producto_id}", status_code=status.HTTP_200_OK, summary="Eliminar un producto")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    """
    Elimina un producto del sistema.
    """
    resultado = ProductoService.eliminar_producto(db, producto_id)
    return resultado
