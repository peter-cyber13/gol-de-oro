"""Inventory service — stock expected calculation, difference detection."""
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import func
from app.extensions import db
from app.models.inventory import InventarioInicial, InventarioDiario
from app.models.order import Pedido, PedidoDetalle
from app.models.purchase import Compra, CompraDetalle
from app.models.product import Producto


def calcular_stock_esperado(producto_id, fecha):
    """
    Stock esperado = último inventario conocido antes o igual a fecha
                    + compras entre última fecha y fecha (inclusive)
                    - pedidos entre última fecha y fecha (inclusive)
    """
    ultimo_diario = db.session.query(InventarioDiario).filter(
        InventarioDiario.producto_id == producto_id,
        InventarioDiario.fecha <= fecha
    ).order_by(InventarioDiario.fecha.desc()).first()

    if ultimo_diario:
        base_cantidad = float(ultimo_diario.cantidad_fisica)
        fecha_base = ultimo_diario.fecha
    else:
        inicial = db.session.query(InventarioInicial).filter(
            InventarioInicial.producto_id == producto_id
        ).first()
        if not inicial:
            return 0.0
        base_cantidad = float(inicial.cantidad)
        fecha_base = inicial.fecha_carga.date() if isinstance(inicial.fecha_carga, datetime) else inicial.fecha_carga

    compras = db.session.query(func.sum(CompraDetalle.cantidad)).join(Compra).filter(
        CompraDetalle.producto_id == producto_id,
        Compra.fecha > fecha_base,
        Compra.fecha <= fecha
    ).scalar() or 0

    pedidos = db.session.query(func.sum(PedidoDetalle.cantidad)).join(Pedido).filter(
        PedidoDetalle.producto_id == producto_id,
        Pedido.fecha > fecha_base,
        Pedido.fecha <= fecha
    ).scalar() or 0

    return float(base_cantidad) + float(compras) - float(pedidos)


def verificar_diferencia(producto_id, fecha):
    """Compare expected stock vs physical count."""
    esperado = calcular_stock_esperado(producto_id, fecha)
    fisico = InventarioDiario.query.filter_by(
        producto_id=producto_id, fecha=fecha
    ).first()
    if not fisico:
        return None
    return {
        'producto_id': producto_id,
        'esperado': round(esperado, 2),
        'fisico': float(fisico.cantidad_fisica),
        'diferencia': round(float(fisico.cantidad_fisica) - esperado, 2)
    }


def producto_tiene_inventario_hoy(producto_id, fecha):
    """Check if product has been counted today."""
    return db.session.query(InventarioDiario.id).filter_by(
        producto_id=producto_id, fecha=fecha
    ).first() is not None


def obtener_ultimo_inventario_conocido(producto_id, fecha):
    """Get the last known stock base for a product."""
    ultimo = db.session.query(InventarioDiario).filter(
        InventarioDiario.producto_id == producto_id,
        InventarioDiario.fecha <= fecha
    ).order_by(InventarioDiario.fecha.desc()).first()

    if ultimo:
        return ultimo
    return db.session.query(InventarioInicial).filter(
        InventarioInicial.producto_id == producto_id
    ).first()