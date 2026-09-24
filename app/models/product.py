"""Producto model."""
from datetime import datetime
from app.extensions import db


class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    unidad_medida = db.Column(db.String(20), nullable=False, default='unidad')
    categoria = db.Column(db.String(30), nullable=False, default='otro')
    frecuencia_inventario = db.Column(db.String(20), default='diario')  # diario | diario_semanal
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # SIN precio, SIN costo

    pedido_detalles = db.relationship('PedidoDetalle', back_populates='producto', lazy='dynamic')
    compra_detalles = db.relationship('CompraDetalle', back_populates='producto', lazy='dynamic')
    inventarios_iniciales = db.relationship('InventarioInicial', back_populates='producto', lazy='dynamic')
    inventarios_diarios = db.relationship('InventarioDiario', back_populates='producto', lazy='dynamic')

    def __init__(self, **kwargs):
        if 'nombre' in kwargs and kwargs['nombre']:
            kwargs['nombre'] = kwargs['nombre'].strip()
            if not kwargs['nombre']:
                raise ValueError("El nombre del producto no puede estar vacío")
        super().__init__(**kwargs)

    def __repr__(self):
        return f'<Producto {self.nombre}>'