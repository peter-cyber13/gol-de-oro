"""Gol de Oro — Seed data for development."""
from datetime import date, datetime, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.extensions import db
from app.models.user import Usuario
from app.models.product import Producto
from app.models.subscription import Suscripcion


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # Admin user
        if not Usuario.query.filter_by(email='admin@goldeoro.com').first():
            admin = Usuario(nombre='Peter', email='admin@goldeoro.com', rol='admin')
            admin.set_password('admin123')
            db.session.add(admin)

        # Encargado
        if not Usuario.query.filter_by(email='encargado@goldeoro.com').first():
            enc = Usuario(nombre='Carlos', email='encargado@goldeoro.com', rol='encargado')
            enc.set_password('encargado123')
            db.session.add(enc)

        # Empleado
        if not Usuario.query.filter_by(email='empleado@goldeoro.com').first():
            emp = Usuario(nombre='Luis', email='empleado@goldeoro.com', rol='empleado')
            emp.set_password('empleado123')
            db.session.add(emp)

        # Products
        productos_data = [
            ('Corona', 'cerveza', 'botella'),
            ('Heineken', 'cerveza', 'botella'),
            ('Victoria', 'cerveza', 'botella'),
            ('Modelo Especial', 'cerveza', 'botella'),
            ('Bacardí Carta Blanca', 'licor', 'botella'),
            ('Bacardí Añejo', 'licor', 'botella'),
            ('Johnnie Walker Red', 'licor', 'botella'),
            ('Johnnie Walker Black', 'licor', 'botella'),
            ('Coca-Cola 600ml', 'refresco', 'botella'),
            ('Coca-Cola Light 600ml', 'refresco', 'botella'),
            ('Sprite 600ml', 'refresco', 'botella'),
            ('Agua Cielo 600ml', 'refresco', 'botella'),
            ('Sabritas Original', 'snack', 'unidad'),
            ('Sabritas Adobadas', 'snack', 'unidad'),
            ('Churrumais', 'snack', 'unidad'),
            ('Cacahuates Japoneses', 'snack', 'unidad'),
        ]

        for nombre, categoria, unidad in productos_data:
            if not Producto.query.filter_by(nombre=nombre).first():
                p = Producto(nombre=nombre, categoria=categoria, unidad_medida=unidad)
                db.session.add(p)

        # Subscription
        if not Suscripcion.query.first():
            sub = Suscripcion(
                cliente_id='gol-de-oro',
                estado='activa',
                fecha_inicio=date.today(),
                fecha_vencimiento=date.today() + timedelta(days=30),
                plan='basico'
            )
            db.session.add(sub)

        db.session.commit()
        print('✅ Seed data created successfully!')
        print('   Admin:     admin@goldeoro.com / admin123')
        print('   Encargado: encargado@goldeoro.com / encargado123')
        print('   Empleado:  empleado@goldeoro.com / empleado123')


if __name__ == '__main__':
    seed()