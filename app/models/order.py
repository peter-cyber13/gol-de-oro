"""Pedido + PedidoDetalle models."""
from datetime import datetime, date, time
from app.extensions import db


class Pedido(db.Model):
    __tablename__ = 'pedidos'

    id = db.Column(db.Integer, primary_key=True)
    folio = db.Column(db.String(30), unique=True, nullable=False, index=True)
    cliente = db.Column(db.String(100), nullable=True)
    fecha = db.Column(db.Date, nullable=False, default=date.today, index=True)
    hora = db.Column(db.Time, nullable=False, default=lambda: datetime.now().time())
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    metodo_ingreso = db.Column(db.String(10), default='manual')  # manual | ocr
    imagen_path = db.Column(db.String(255), nullable=True)

    detalles = db.relationship('PedidoDetalle', backref='pedido',
                               lazy='joined', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Pedido {self.folio}>'


class PedidoDetalle(db.Model):
    __tablename__ = 'pedido_detalles'

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)

    producto = db.relationship('Producto', back_populates='pedido_detalles', lazy='joined')

    def __init__(self, **kwargs):
        if 'cantidad' in kwargs and kwargs['cantidad'] is not None:
            try:
                val = float(kwargs['cantidad'])
                if val <= 0:
                    raise ValueError("La cantidad debe ser mayor a 0")
            except (TypeError, ValueError) as e:
                if 'must be greater than 0' not in str(e):
                    raise ValueError("La cantidad debe ser un número válido mayor a 0")
                raise
        super().__init__(**kwargs)

    def __repr__(self):
        return f'<PedidoDetalle pedido={self.pedido_id} prod={self.producto_id} qty={self.cantidad}>'


class SolicitudModificacion(db.Model):
    __tablename__ = 'solicitudes_modificacion'

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    usuario_solicita_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    usuario_aprueba_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    productos_json = db.Column(db.Text, nullable=False)  # JSON con lista de productos
    estado = db.Column(db.String(20), nullable=False, default='pendiente')  # pendiente | aprobado | rechazado
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_respuesta = db.Column(db.DateTime, nullable=True)

    pedido = db.relationship('Pedido', backref='solicitudes_modificacion', lazy='joined')
    solicitante = db.relationship('Usuario', foreign_keys=[usuario_solicita_id], lazy='joined')
    aprobador = db.relationship('Usuario', foreign_keys=[usuario_aprueba_id], lazy='joined')

    def __repr__(self):
        return f'<SolicitudModificacion pedido={self.pedido_id} estado={self.estado}>'