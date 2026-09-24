"""CierreDiario model."""
from datetime import datetime
from app.extensions import db


class CierreDiario(db.Model):
    __tablename__ = 'cierres_diarios'

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, unique=True, nullable=False, index=True)
    usuario_encargado_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    productos_correctos = db.Column(db.Integer, default=0)
    productos_con_diferencia = db.Column(db.Integer, default=0)
    diferencia_detectada = db.Column(db.Text)  # JSON string
    notificado_app = db.Column(db.Boolean, default=False)
    fecha_cierre = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CierreDiario {self.fecha}>'