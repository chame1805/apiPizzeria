from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.data.sources.database import Base # Importamos la base que acabamos de arreglar

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    nombre = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.now)

class Cliente(Base):
    __tablename__ = 'clientes'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    telefono = Column(String)
    direccion = Column(String, nullable=False)
    
    ordenes = relationship("Orden", back_populates="cliente")

class Producto(Base):
    __tablename__ = 'productos'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    precio = Column(Float, nullable=False)

class Orden(Base):
    __tablename__ = 'ordenes'

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    fecha = Column(DateTime, default=datetime.now)
    total_venta = Column(Float, nullable=False)
    pago_cliente = Column(Float, nullable=False)
    cambio = Column(Float, nullable=False)
    estatus = Column(String, default="PAGADA") 

    cliente = relationship("Cliente", back_populates="ordenes")
    detalles = relationship("DetalleOrden", back_populates="orden")

class DetalleOrden(Base):
    __tablename__ = 'detalles_orden'

    id = Column(Integer, primary_key=True, index=True)
    orden_id = Column(Integer, ForeignKey('ordenes.id'))
    producto_id = Column(Integer, ForeignKey('productos.id'))
    cantidad = Column(Integer, default=1)
    subtotal = Column(Float)

    orden = relationship("Orden", back_populates="detalles")
    producto = relationship("Producto")