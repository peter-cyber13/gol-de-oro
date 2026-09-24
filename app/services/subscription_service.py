"""Subscription service — SAAS logic."""
from datetime import date
from app.extensions import db
from app.models.subscription import Suscripcion


def get_subscription():
    """Get the current subscription."""
    sub = Suscripcion.query.first()
    if not sub:
        # Create default subscription
        from datetime import timedelta
        sub = Suscripcion(
            cliente_id='gol-de-oro',
            estado='activa',
            fecha_inicio=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=30),
            plan='basico'
        )
        db.session.add(sub)
        db.session.commit()
    return sub


def verificar_vencimiento():
    """
    Check subscription expiry. Run daily (cron).
    Returns dict with status changes.
    """
    sub = get_subscription()
    result = {'aviso': False, 'suspendida': False}

    dias_restantes = (sub.fecha_vencimiento - date.today()).days

    if 0 <= dias_restantes <= 7 and not sub.aviso_enviado_7d:
        sub.aviso_enviado_7d = True
        result['aviso'] = True

    if date.today() > sub.fecha_vencimiento and sub.estado == 'activa':
        sub.estado = 'suspendida'
        result['suspendida'] = True

    db.session.commit()
    return result


def registrar_pago(dias_extension=30):
    """Mark payment received and extend subscription."""
    from datetime import timedelta
    sub = get_subscription()
    sub.estado = 'activa'
    sub.ultimo_pago = date.today()
    sub.fecha_vencimiento = date.today() + timedelta(days=dias_extension)
    sub.aviso_enviado_7d = False
    db.session.commit()
    return sub