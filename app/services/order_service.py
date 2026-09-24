"""Order service — create orders with inventory deduction."""
from datetime import date, datetime, time
from decimal import Decimal
from app.extensions import db
from app.models.order import Pedido, PedidoDetalle
from app.models.product import Producto


def generar_folio(fecha):
    """Generate unique folio with concurrency protection."""
    prefix = f"P-{fecha.strftime('%Y%m%d')}-"

    for intento in range(10):
        ultimo = db.session.query(Pedido.folio).filter(
            Pedido.folio.like(f"{prefix}%")
        ).order_by(Pedido.folio.desc()).with_for_update().first()

        num = 1
        if ultimo:
            try:
                num = int(ultimo.folio.split('-')[-1]) + 1
            except (ValueError, IndexError):
                num = 1

        folio = f"{prefix}{num:03d}"

        existe = db.session.query(Pedido.id).filter_by(folio=folio).first()
        if not existe:
            return folio

        db.session.rollback()

    import time
    timestamp = int(time.time() * 1000) % 100000
    return f"{prefix}{timestamp}"


def crear_pedido(usuario_id, fecha, cliente, productos):
    """
    Create a pedido with its detalles.
    productos: list of dicts [{'id': int, 'cantidad': numeric}, ...]
    """
    if not productos:
        raise ValueError("No se puede crear un pedido sin productos")

    # Validate productos
    for p in productos:
        if not p.get('id') or not p.get('cantidad'):
            raise ValueError("Cada producto debe tener id y cantidad")
        if float(p['cantidad']) <= 0:
            raise ValueError("Las cantidades deben ser mayores a 0")

        producto = db.session.query(Producto).filter_by(
            id=p['id'], activo=True
        ).first()
        if not producto:
            raise ValueError(f"Producto ID {p['id']} no encontrado o inactivo")

    try:
        folio = generar_folio(fecha)

        pedido = Pedido(
            folio=folio,
            cliente=cliente.strip() if cliente and cliente.strip() else None,
            fecha=fecha,
            hora=datetime.now().time(),
            usuario_id=usuario_id
        )
        db.session.add(pedido)
        db.session.flush()

        for p in productos:
            detalle = PedidoDetalle(
                pedido_id=pedido.id,
                producto_id=int(p['id']),
                cantidad=Decimal(str(p['cantidad']))
            )
            db.session.add(detalle)

        db.session.commit()
        return pedido

    except Exception as e:
        db.session.rollback()
        raise


def obtener_pedidos(fecha=None, limite=100):
    """List pedidos, optionally filtered by date."""
    query = Pedido.query.order_by(Pedido.fecha.desc(), Pedido.id.desc())
    if fecha:
        query = query.filter(Pedido.fecha == fecha)
    return query.limit(limite).all()


def unidades_despachadas(producto_id, fecha_desde, fecha_hasta):
    """Total units of a product sold in pedidos between dates."""
    from sqlalchemy import func
    total = db.session.query(func.sum(PedidoDetalle.cantidad)).join(Pedido).filter(
        PedidoDetalle.producto_id == producto_id,
        Pedido.fecha >= fecha_desde,
        Pedido.fecha <= fecha_hasta
    ).scalar() or 0
    return float(total)