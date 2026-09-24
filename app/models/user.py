"""Usuario model."""
from datetime import datetime, timedelta
import uuid
from flask_login import UserMixin
from app.extensions import db, bcrypt


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='empleado')  # admin | encargado | empleado
    activo = db.Column(db.Boolean, default=True)
    password_reset_token = db.Column(db.String(128), nullable=True)
    password_reset_expires = db.Column(db.DateTime, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime, nullable=True)

    # Relationships
    pedidos = db.relationship('Pedido', backref='usuario', lazy='dynamic')
    compras = db.relationship('Compra', backref='usuario', lazy='dynamic')
    inventarios_diarios = db.relationship('InventarioDiario', backref='usuario', lazy='dynamic')
    inventarios_iniciales = db.relationship('InventarioInicial', backref='usuario', lazy='dynamic')
    cierres = db.relationship('CierreDiario', backref='usuario_encargado', lazy='dynamic')
    notificaciones = db.relationship('Notificacion', backref='usuario', lazy='dynamic')

    def set_password(self, pw):
        self.password_hash = bcrypt.generate_password_hash(pw).decode('utf-8')

    def check_password(self, pw):
        return bcrypt.check_password_hash(self.password_hash, pw)

    def generar_reset_token(self):
        self.password_reset_token = str(uuid.uuid4())
        self.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        return self.password_reset_token

    def validar_reset_token(self, token):
        return (self.password_reset_token == token
                and self.password_reset_expires
                and self.password_reset_expires > datetime.utcnow())

    def limpiar_reset_token(self):
        self.password_reset_token = None
        self.password_reset_expires = None

    def __repr__(self):
        return f'<Usuario {self.nombre} ({self.rol})>'