"""Notificacion model."""
from datetime import datetime
from app.extensions import db


class Notificacion(db.Model):
    __tablename__ = 'notificaciones'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    tipo = db.Column(db.String(30))  # cierre_realizado | recordatorio | sistema
    mensaje = db.Column(db.Text)
    leida = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notificacion {self.tipo} leida={self.leida}>'