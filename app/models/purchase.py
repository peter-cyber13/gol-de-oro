"""Compra + CompraDetalle models."""
from datetime import datetime, date
from app.extensions import db


class Compra(db.Model):
    __tablename__ = 'compras'

    id = db.Column(db.Integer, primary_key=True)
    folio_compra = db.Column(db.String(50))
    proveedor = db.Column(db.String(100))
    fecha = db.Column(db.Date, default=date.today, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    detalles = db.relationship('CompraDetalle', backref='compra',
                               lazy='joined', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Compra {self.folio_compra or f"C-{self.id}"}>'


class CompraDetalle(db.Model):
    __tablename__ = 'compra_detalles'

    id = db.Column(db.Integer, primary_key=True)
    compra_id = db.Column(db.Integer, db.ForeignKey('compras.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    cantidad = db.Column(db.Numeric(10, 2))

    producto = db.relationship('Producto', back_populates='compra_detalles', lazy='joined')

    def __repr__(self):
        return f'<CompraDetalle compra={self.compra_id} prod={self.producto_id} qty={self.cantidad}>'