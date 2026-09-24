"""Helper utilities."""
from datetime import date


def formatear_fecha(fecha):
    """Format date for display."""
    if isinstance(fecha, date):
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        return f"{fecha.day} de {meses[fecha.month - 1]}, {fecha.year}"
    return str(fecha)


def formatear_hora(hora):
    """Format time for display (HH:MM)."""
    if hora:
        return hora.strftime('%H:%M')
    return ''


def resumir_texto(texto, max_len=100):
    """Truncate text with ellipsis."""
    if not texto:
        return ''
    if len(texto) <= max_len:
        return texto
    return texto[:max_len].rsplit(' ', 1)[0] + '…'


def icono_categoria(categoria):
    """Get an emoji icon for a product category."""
    icons = {
        'cerveza': '🍺',
        'licor': '🥃',
        'refresco': '🥤',
        'snack': '🍿',
        'otro': '📦',
    }
    return icons.get(categoria, '📦')


def from_json(value):
    """Parse JSON string for Jinja2 templates."""
    import json
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []