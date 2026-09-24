"""Blueprint registration."""
from flask import Flask


def register_routes(app: Flask):
    from app.routes.auth import auth_bp
    from app.routes.orders import orders_bp
    from app.routes.inventory import inventory_bp
    from app.routes.purchases import purchases_bp
    from app.routes.close import close_bp
    from app.routes.reports import reports_bp
    from app.routes.admin import admin_bp
    from app.routes.notifications import notifications_bp
    from app.routes.orders import aprobaciones_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(close_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(aprobaciones_bp)