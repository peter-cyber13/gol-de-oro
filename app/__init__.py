"""Gol de Oro app factory."""
from flask import Flask, redirect, url_for, render_template
from .config import get_config
from .extensions import db, login_manager, bcrypt, mail, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message = 'Inicia sesión para acceder.'
    bcrypt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    from .models import (Usuario, Producto, Pedido, PedidoDetalle, SolicitudModificacion,
                         Compra, CompraDetalle, InventarioInicial,
                         InventarioDiario, CierreDiario,
                         Notificacion, Suscripcion)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    from .routes import register_routes
    register_routes(app)

    from .utils.subscription_middleware import setup_middleware
    setup_middleware(app)

    from .utils import helpers
    app.jinja_env.globals.update(
        formatear_fecha=helpers.formatear_fecha,
        formatear_hora=helpers.formatear_hora,
        icono_categoria=helpers.icono_categoria,
        resumir_texto=helpers.resumir_texto,
    )
    app.jinja_env.filters['from_json'] = helpers.from_json

    # Dashboard / home
    from flask_login import login_required, current_user

    @app.route('/')
    @login_required
    def index():
        from datetime import date
        from app.models.order import Pedido
        from app.models.inventory import InventarioDiario
        from app.models.daily_close import CierreDiario
        from app.models.notification import Notificacion

        today = date.today()
        pedidos_hoy = Pedido.query.filter(Pedido.fecha == today).count()
        inventario_hoy = InventarioDiario.query.filter_by(fecha=today).count()
        tiene_cierre = CierreDiario.query.filter_by(fecha=today).first() is not None
        no_leidas = Notificacion.query.filter_by(
            usuario_id=current_user.id, leida=False
        ).count()

        return render_template(
            'dashboard.html',
            pedidos_hoy=pedidos_hoy,
            inventario_hoy=inventario_hoy,
            tiene_cierre=tiene_cierre,
            no_leidas=no_leidas,
            today=today
        )

    @app.route('/suspendido')
    def suspended():
        return render_template('suspended.html')

    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        from app.models.notification import Notificacion
        no_leidas = 0
        if current_user.is_authenticated:
            no_leidas = Notificacion.query.filter_by(
                usuario_id=current_user.id, leida=False
            ).count()
        return {
            'now_year': __import__('datetime').datetime.now().year,
            'no_leidas': no_leidas,
        }

    return app