"""Suscripcion model."""
from datetime import datetime
from app.extensions import db


class Suscripcion(db.Model):
    __tablename__ = 'suscripciones'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.String(50), default='gol-de-oro')
    estado = db.Column(db.String(20), default='activa')  # activa | suspendida | cancelada
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    ultimo_pago = db.Column(db.Date)
    aviso_enviado_7d = db.Column(db.Boolean, default=False)
    plan = db.Column(db.String(20), default='basico')  # basico | pro | ilimitado

    def __repr__(self):
        return f'<Suscripcion {self.cliente_id} {self.estado}>'