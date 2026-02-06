from sqlalchemy.orm import Session
from typing import List, Optional
from app.domain.models.models import Cliente, Orden, DetalleOrden, Producto

class OrdenRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener_o_crear_cliente(self, datos_cliente) -> Cliente:
        # 1. Buscamos si el cliente ya existe por teléfono
        cliente = self.db.query(Cliente).filter(Cliente.telefono == datos_cliente.telefono).first()
        
        # 2. Si no existe, lo creamos
        if not cliente:
            cliente = Cliente(
                nombre=datos_cliente.nombre,
                telefono=datos_cliente.telefono,
                direccion=datos_cliente.direccion
            )
            self.db.add(cliente)
            self.db.commit()
            self.db.refresh(cliente)
        
        return cliente

    def obtener_precio_producto(self, producto_id: int) -> float:
        producto = self.db.query(Producto).filter(Producto.id == producto_id).first()
        if producto:
            return producto.precio
        return 0.0

    def guardar_orden(self, orden: Orden, detalles: list[DetalleOrden]) -> Orden:
        # 1. Guardamos la cabecera de la orden
        self.db.add(orden)
        self.db.commit()
        self.db.refresh(orden) # Esto nos da el ID generado (folio)

        # 2. Asignamos ese ID a cada detalle y guardamos
        for d in detalles:
            d.orden_id = orden.id
            self.db.add(d)
        
        self.db.commit()
        return orden
    
    def obtener_todas_ordenes(self) -> List[Orden]:
        """Obtiene todas las órdenes con sus relaciones"""
        return self.db.query(Orden).all()
    
    def obtener_orden_por_id(self, orden_id: int) -> Optional[Orden]:
        """Obtiene una orden específica por ID"""
        return self.db.query(Orden).filter(Orden.id == orden_id).first()
    
    def eliminar_orden(self, orden_id: int) -> bool:
        """Elimina una orden y sus detalles"""
        orden = self.obtener_orden_por_id(orden_id)
        if not orden:
            return False
        
        # Primero eliminar los detalles
        self.db.query(DetalleOrden).filter(DetalleOrden.orden_id == orden_id).delete()
        
        # Luego eliminar la orden
        self.db.delete(orden)
        self.db.commit()
        return True