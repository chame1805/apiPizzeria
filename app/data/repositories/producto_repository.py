from sqlalchemy.orm import Session
from app.domain.models.models import Producto
from typing import List, Optional

class ProductoRepository:
    
    @staticmethod
    def obtener_todos(db: Session) -> List[Producto]:
        """Obtiene todos los productos"""
        return db.query(Producto).all()
    
    @staticmethod
    def obtener_por_id(db: Session, producto_id: int) -> Optional[Producto]:
        """Obtiene un producto por ID"""
        return db.query(Producto).filter(Producto.id == producto_id).first()
    
    @staticmethod
    def obtener_por_nombre(db: Session, nombre: str) -> Optional[Producto]:
        """Obtiene un producto por nombre"""
        return db.query(Producto).filter(Producto.nombre == nombre).first()
    
    @staticmethod
    def crear_producto(db: Session, nombre: str, precio: float) -> Producto:
        """Crea un nuevo producto"""
        producto = Producto(nombre=nombre, precio=precio)
        db.add(producto)
        db.commit()
        db.refresh(producto)
        return producto
    
    @staticmethod
    def actualizar_producto(db: Session, producto_id: int, nombre: Optional[str] = None, precio: Optional[float] = None) -> Optional[Producto]:
        """Actualiza un producto existente"""
        producto = ProductoRepository.obtener_por_id(db, producto_id)
        if not producto:
            return None
        
        if nombre is not None:
            producto.nombre = nombre
        if precio is not None:
            producto.precio = precio
        
        db.commit()
        db.refresh(producto)
        return producto
    
    @staticmethod
    def eliminar_producto(db: Session, producto_id: int) -> bool:
        """Elimina un producto"""
        producto = ProductoRepository.obtener_por_id(db, producto_id)
        if not producto:
            return False
        
        db.delete(producto)
        db.commit()
        return True
