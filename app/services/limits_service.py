"""Plan limits service for Plan Básico."""
from datetime import date, timedelta
from app.extensions import db
from app.models.user import Usuario
from app.models.product import Producto

MAX_USUARIOS = 2
MAX_PRODUCTOS = 300
DIAS_HISTORIAL = 90


class LimiteAlcanzado(Exception):
    pass


def verificar_limite_usuarios():
    """Raise if at max active users."""
    if Usuario.query.filter_by(activo=True).count() >= MAX_USUARIOS:
        raise LimiteAlcanzado(
            f"Límite alcanzado: máximo {MAX_USUARIOS} usuarios activos en el plan actual. "
            "Desactiva un usuario o actualiza tu plan."
        )


def verificar_limite_productos():
    """Raise if at max active products."""
    if Producto.query.filter_by(activo=True).count() >= MAX_PRODUCTOS:
        raise LimiteAlcanzado(
            f"Límite alcanzado: máximo {MAX_PRODUCTOS} productos activos en el plan actual. "
            "Desactiva productos o actualiza tu plan."
        )


def filtrar_historial_reportes(query, columna_fecha):
    """
    Filter queries to only show last 3 months.
    NOT for stock calculations — those need complete data.
    """
    limite = date.today() - timedelta(days=DIAS_HISTORIAL)
    return query.filter(columna_fecha >= limite)


def obtener_datos_completos(query):
    """For stock calculations that need full data."""
    return query


def get_usage_stats():
    """Get current usage stats for admin dashboard."""
    usuarios = Usuario.query.filter_by(activo=True).count()
    productos = Producto.query.filter_by(activo=True).count()
    return {
        'usuarios': usuarios,
        'usuarios_max': MAX_USUARIOS,
        'usuarios_pct': round(usuarios / MAX_USUARIOS * 100),
        'productos': productos,
        'productos_max': MAX_PRODUCTOS,
        'productos_pct': round(productos / MAX_PRODUCTOS * 100),
        'historial_dias': DIAS_HISTORIAL,
    }