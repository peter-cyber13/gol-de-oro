"""Reset admin password."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.extensions import db
from app.models.user import Usuario


def reset_admin(email='admin@goldeoro.com', password='admin123'):
    app = create_app()
    with app.app_context():
        admin = Usuario.query.filter_by(email=email).first()
        if not admin:
            admin = Usuario(nombre='Admin', email=email, rol='admin')
            db.session.add(admin)
        admin.set_password(password)
        admin.activo = True
        admin.password_reset_token = None
        admin.password_reset_expires = None
        db.session.commit()
        print(f'✅ Admin password reset for {email}')


if __name__ == '__main__':
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else 'admin@goldeoro.com'
    password = sys.argv[2] if len(sys.argv) > 2 else 'admin123'
    reset_admin(email, password)