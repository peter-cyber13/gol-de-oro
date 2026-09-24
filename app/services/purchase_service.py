"""Purchase service — create purchases that increment inventory."""
from datetime import date, datetime
from decimal import Decimal
from app.extensions import db
from app.models.purchase import Compra, CompraDetalle
from app.models.product import Producto


def crear_compra(usuario_id, fecha, proveedor, folio_compra, productos):
    """
    Create a purchase with its detalles.
    productos: list of dicts [{'id': int, 'cantidad': numeric}, ...]
    """
    if not productos:
        raise ValueError("No se puede crear una compra sin productos")

    for p in productos:
        if not p.get('id') or not p.get('cantidad'):
            raise ValueError("Cada producto debe tener id y cantidad")
        if float(p['cantidad']) <= 0:
            raise ValueError("Las cantidades deben ser mayores a 0")

        producto = db.session.query(Producto).filter_by(id=p['id'], activo=True).first()
        if not producto:
            raise ValueError(f"Producto ID {p['id']} no encontrado o inactivo")

    try:
        compra = Compra(
            folio_compra=folio_compra.strip() if folio_compra else None,
            proveedor=proveedor.strip() if proveedor else None,
            fecha=fecha,
            usuario_id=usuario_id
        )
        db.session.add(compra)
        db.session.flush()

        for p in productos:
            detalle = CompraDetalle(
                compra_id=compra.id,
                producto_id=int(p['id']),
                cantidad=Decimal(str(p['cantidad']))
            )
            db.session.add(detalle)

        db.session.commit()
        return compra

    except Exception as e:
        db.session.rollback()
        raise


def obtener_compras(fecha_desde=None, fecha_hasta=None, limite=100):
    """List purchases with optional date filter."""
    query = Compra.query.order_by(Compra.fecha.desc(), Compra.id.desc())
    if fecha_desde:
        query = query.filter(Compra.fecha >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Compra.fecha <= fecha_hasta)
    return query.limit(limite).all()