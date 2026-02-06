from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.data.repositories.producto_repository import ProductoRepository
from app.domain.schemas.producto_schemas import ProductoCreate, ProductoUpdate
from app.domain.models.models import Producto
from typing import List

class ProductoService:
    
    @staticmethod
    def listar_productos(db: Session) -> List[Producto]:
        """Obtiene todos los productos"""
        return ProductoRepository.obtener_todos(db)
    
    @staticmethod
    def obtener_producto(db: Session, producto_id: int) -> Producto:
        """Obtiene un producto por ID"""
        producto = ProductoRepository.obtener_por_id(db, producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {producto_id} no encontrado"
            )
        return producto
    
    @staticmethod
    def crear_producto(db: Session, datos: ProductoCreate) -> Producto:
        """Crea un nuevo producto"""
        # Verificar si ya existe un producto con ese nombre
        producto_existente = ProductoRepository.obtener_por_nombre(db, datos.nombre)
        if producto_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un producto con el nombre '{datos.nombre}'"
            )
        
        try:
            producto = ProductoRepository.crear_producto(
                db=db,
                nombre=datos.nombre,
                precio=datos.precio
            )
            return producto
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear producto: {str(e)}"
            )
    
    @staticmethod
    def actualizar_producto(db: Session, producto_id: int, datos: ProductoUpdate) -> Producto:
        """Actualiza un producto existente"""
        # Verificar que el producto existe
        producto_existente = ProductoRepository.obtener_por_id(db, producto_id)
        if not producto_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {producto_id} no encontrado"
            )
        
        # Si se está actualizando el nombre, verificar que no exista otro producto con ese nombre
        if datos.nombre and datos.nombre != producto_existente.nombre:
            producto_con_nombre = ProductoRepository.obtener_por_nombre(db, datos.nombre)
            if producto_con_nombre:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un producto con el nombre '{datos.nombre}'"
                )
        
        try:
            producto = ProductoRepository.actualizar_producto(
                db=db,
                producto_id=producto_id,
                nombre=datos.nombre,
                precio=datos.precio
            )
            return producto
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar producto: {str(e)}"
            )
    
    @staticmethod
    def eliminar_producto(db: Session, producto_id: int) -> dict:
        """Elimina un producto"""
        # Verificar que el producto existe
        producto = ProductoRepository.obtener_por_id(db, producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {producto_id} no encontrado"
            )
        
        try:
            eliminado = ProductoRepository.eliminar_producto(db, producto_id)
            if eliminado:
                return {"mensaje": f"Producto '{producto.nombre}' eliminado exitosamente"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error al eliminar el producto"
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar producto: {str(e)}"
            )
