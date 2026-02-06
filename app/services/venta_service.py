from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List
from app.data.repositories.orden_repository import OrdenRepository
from app.domain.models.models import Orden, DetalleOrden
from app.domain.schemas.schemas import VentaCreate, VentaResponse
from app.domain.schemas.venta_schemas import OrdenResponse, DetalleOrdenResponse

class VentaService:
    def __init__(self, db: Session):
        self.repo = OrdenRepository(db)

    def registrar_venta(self, datos: VentaCreate) -> VentaResponse:
        # 1. Calcular el Total
        total_calculado = 0.0
        lista_detalles_bd = []

        for item in datos.items:
            precio_unitario = self.repo.obtener_precio_producto(item.producto_id)
            
            # Validación: ¿Existe la pizza?
            if precio_unitario == 0:
                raise HTTPException(status_code=400, detail=f"El producto ID {item.producto_id} no existe")
            
            subtotal = precio_unitario * item.cantidad
            total_calculado += subtotal
            
            # Preparamos el objeto detalle para la BD
            detalle = DetalleOrden(
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                subtotal=subtotal
            )
            lista_detalles_bd.append(detalle)

        # 2. Validar Pago
        if datos.pago_cliente < total_calculado:
            raise HTTPException(status_code=400, detail="Dinero insuficiente para pagar")

        cambio = datos.pago_cliente - total_calculado

        # 3. Gestionar Cliente (Busca o Crea)
        cliente_bd = self.repo.obtener_o_crear_cliente(datos.cliente)

        # 4. Crear Objeto Orden
        nueva_orden = Orden(
            cliente_id=cliente_bd.id,
            total_venta=total_calculado,
            pago_cliente=datos.pago_cliente,
            cambio=cambio
        )

        # 5. Guardar todo en BD
        orden_guardada = self.repo.guardar_orden(nueva_orden, lista_detalles_bd)

        # 6. Retornar el Ticket
        return VentaResponse(
            folio=orden_guardada.id,
            cliente=cliente_bd.nombre,
            fecha=str(datetime.now()),
            total=total_calculado,
            pago=datos.pago_cliente,
            cambio=cambio,
            mensaje="¡Venta Exitosa! 🍕"
        )
    
    def obtener_historial(self) -> List[OrdenResponse]:
        """Obtiene el historial de todas las órdenes"""
        ordenes = self.repo.obtener_todas_ordenes()
        resultado = []
        
        for orden in ordenes:
            detalles = [
                DetalleOrdenResponse(
                    producto_id=detalle.producto_id,
                    producto_nombre=detalle.producto.nombre,
                    cantidad=detalle.cantidad,
                    precio_unitario=detalle.producto.precio,
                    subtotal=detalle.subtotal
                )
                for detalle in orden.detalles
            ]
            
            resultado.append(OrdenResponse(
                id=orden.id,
                cliente_nombre=orden.cliente.nombre,
                fecha=orden.fecha.isoformat() if orden.fecha else None,
                total_venta=orden.total_venta,
                pago_cliente=orden.pago_cliente,
                cambio=orden.cambio,
                estatus=orden.estatus,
                detalles=detalles
            ))
        
        return resultado
    
    def obtener_orden_por_id(self, orden_id: int) -> OrdenResponse:
        """Obtiene una orden específica por ID"""
        orden = self.repo.obtener_orden_por_id(orden_id)
        
        if not orden:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden con ID {orden_id} no encontrada"
            )
        
        detalles = [
            DetalleOrdenResponse(
                producto_id=detalle.producto_id,
                producto_nombre=detalle.producto.nombre,
                cantidad=detalle.cantidad,
                precio_unitario=detalle.producto.precio,
                subtotal=detalle.subtotal
            )
            for detalle in orden.detalles
        ]
        
        return OrdenResponse(
            id=orden.id,
            cliente_nombre=orden.cliente.nombre,
            fecha=orden.fecha.isoformat() if orden.fecha else None,
            total_venta=orden.total_venta,
            pago_cliente=orden.pago_cliente,
            cambio=orden.cambio,
            estatus=orden.estatus,
            detalles=detalles
        )
    
    def eliminar_orden(self, orden_id: int) -> dict:
        """Elimina una orden del sistema"""
        orden = self.repo.obtener_orden_por_id(orden_id)
        
        if not orden:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden con ID {orden_id} no encontrada"
            )
        
        try:
            eliminado = self.repo.eliminar_orden(orden_id)
            if eliminado:
                return {"mensaje": f"Orden #{orden_id} eliminada exitosamente"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error al eliminar la orden"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar orden: {str(e)}"
            )