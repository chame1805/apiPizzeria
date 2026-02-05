from fastapi import HTTPException
from datetime import datetime
from sqlalchemy.orm import Session
from app.data.repositories.orden_repository import OrdenRepository
from app.domain.models.models import Orden, DetalleOrden
from app.domain.schemas.schemas import VentaCreate, VentaResponse

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