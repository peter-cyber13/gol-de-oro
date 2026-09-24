"""Auth service — login, password reset."""
from datetime import datetime
from app.extensions import db
from app.models.user import Usuario


def autenticar(email, password):
    """Authenticate user by email and password. Returns user or None."""
    usuario = Usuario.query.filter_by(email=email, activo=True).first()
    if usuario and usuario.check_password(password):
        usuario.ultimo_acceso = datetime.utcnow()
        db.session.commit()
        return usuario
    return None


def iniciar_recuperacion(email):
    """Generate reset token for user. Returns token or None."""
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return None
    token = usuario.generar_reset_token()
    db.session.commit()
    return token


def completar_recuperacion(token, nueva_password):
    """Validate token and set new password. Returns user or None."""
    usuario = Usuario.query.filter_by(password_reset_token=token).first()
    if not usuario or not usuario.validar_reset_token(token):
        return None
    usuario.set_password(nueva_password)
    usuario.limpiar_reset_token()
    db.session.commit()
    return usuario


def listar_usuarios_activos():
    """Count of active users (for plan limits)."""
    return Usuario.query.filter_by(activo=True).count()


def crear_usuario(nombre, email, password, rol='empleado'):
    """Create new user. Validates plan limits."""
    from app.services.limits_service import verificar_limite_usuarios
    verificar_limite_usuarios()
    usuario = Usuario(nombre=nombre.strip(), email=email.strip().lower(), rol=rol)
    usuario.set_password(password)
    db.session.add(usuario)
    db.session.commit()
    return usuario