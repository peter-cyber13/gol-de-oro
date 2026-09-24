"""Subscription middleware — check SAAS status on each request."""
from flask import request, render_template
from flask_login import current_user
from app.models.subscription import Suscripcion


def setup_middleware(app):
    """Register before_request handler for SAAS suspension."""

    @app.before_request
    def verificar_suscripcion():
        # Public routes always accessible
        if request.endpoint in ('static', 'auth_bp.login', 'auth_bp.recover_form',
                                'auth_bp.reset_password', 'auth_bp.api_recuperar',
                                'auth_bp.api_cambiar_pass', 'suspended', 'auth_bp.logout'):
            return None

        # Not authenticated — let them try to log in
        if not current_user.is_authenticated:
            return None

        # Admin always passes
        if hasattr(current_user, 'rol') and current_user.rol == 'admin':
            return None

        # Check subscription for non-admin users
        if hasattr(current_user, 'rol'):
            sub = Suscripcion.query.first()
            if sub and sub.estado == 'suspendida':
                return render_template('suspended.html'), 403

        return None