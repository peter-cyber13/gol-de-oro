"""Inventory models: InventarioInicial + InventarioDiario."""
from datetime import datetime, date
from app.extensions import db


class InventarioInicial(db.Model):
    __tablename__ = 'inventario_inicial'

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    cantidad = db.Column(db.Numeric(10, 2))
    fecha_carga = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))

    producto = db.relationship('Producto', back_populates='inventarios_iniciales', lazy='joined')

    def __repr__(self):
        return f'<InventarioInicial prod={self.producto_id} qty={self.cantidad}>'


class InventarioDiario(db.Model):
    __tablename__ = 'inventario_diario'

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    cantidad_fisica = db.Column(db.Numeric(10, 2))
    fecha = db.Column(db.Date, nullable=False, default=date.today)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    producto = db.relationship('Producto', back_populates='inventarios_diarios', lazy='joined')

    __table_args__ = (
        db.UniqueConstraint('producto_id', 'fecha', name='uq_inventario_producto_fecha'),
        db.Index('idx_inventario_fecha', 'fecha'),
        db.Index('idx_inventario_producto', 'producto_id'),
    )

    def __repr__(self):
        return f'<InventarioDiario prod={self.producto_id} fecha={self.fecha} qty={self.cantidad_fisica}>'