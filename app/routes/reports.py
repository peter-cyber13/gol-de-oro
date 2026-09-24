"""Reports routes — on-demand reports."""
from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.product import Producto
from app.models.order import Pedido, PedidoDetalle
from app.models.purchase import Compra, CompraDetalle
from app.models.inventory import InventarioDiario
from app.models.daily_close import CierreDiario
from app.models.notification import Notificacion
from app.services.inventory_service import calcular_stock_esperado
from app.services.limits_service import filtrar_historial_reportes
from app.utils.decorators import encargado_required

reports_bp = Blueprint('reports_bp', __name__, url_prefix='/reportes')


def parse_date_range():
    """Parse 'desde' and 'hasta' from request args."""
    desde_str = request.args.get('desde', '')
    hasta_str = request.args.get('hasta', '')
    desde = hasta = None

    if desde_str:
        try:
            desde = datetime.strptime(desde_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    if hasta_str:
        try:
            hasta = datetime.strptime(hasta_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    # Default to last 30 days
    if not desde:
        desde = date.today() - timedelta(days=30)
    if not hasta:
        hasta = date.today()

    return desde, hasta


@reports_bp.route('', methods=['GET'])
@login_required
@encargado_required
def index():
    """Reports dashboard."""
    return render_template('reports/index.html')


@reports_bp.route('/inventario-actual', methods=['GET'])
@login_required
@encargado_required
def inventario_actual():
    """Current stock of all products."""
    productos = Producto.query.filter_by(activo=True).order_by(
        Producto.categoria, Producto.nombre
    ).all()

    stock_data = []
    for p in productos:
        esperado = calcular_stock_esperado(p.id, date.today())
        stock_data.append({
            'producto': p,
            'stock_esperado': round(esperado, 2)
        })

    return render_template('reports/current_stock.html', stock_data=stock_data)


@reports_bp.route('/pedidos', methods=['GET'])
@login_required
@encargado_required
def pedidos():
    """Orders report with date range."""
    desde, hasta = parse_date_range()

    from sqlalchemy import func
    query = db.session.query(
        Producto.id,
        Producto.nombre,
        Producto.categoria,
        func.sum(PedidoDetalle.cantidad).label('total'),
        func.count(func.distinct(Pedido.id)).label('pedidos_count')
    ).join(PedidoDetalle, Producto.id == PedidoDetalle.producto_id
    ).join(Pedido, PedidoDetalle.pedido_id == Pedido.id
    ).filter(
        Pedido.fecha >= desde,
        Pedido.fecha <= hasta
    ).group_by(Producto.id, Producto.nombre, Producto.categoria
    ).order_by(func.sum(PedidoDetalle.cantidad).desc()).all()

    return render_template('reports/pedidos.html',
                           desde=desde, hasta=hasta,
                           productos=query)


@reports_bp.route('/compras', methods=['GET'])
@login_required
@encargado_required
def compras():
    """Purchases report."""
    desde, hasta = parse_date_range()
    compras = Compra.query.filter(
        Compra.fecha >= desde,
        Compra.fecha <= hasta
    ).order_by(Compra.fecha.desc()).all()
    return render_template('reports/compras.html',
                           desde=desde, hasta=hasta,
                           compras=compras)


@reports_bp.route('/diferencias', methods=['GET'])
@login_required
@encargado_required
def diferencias():
    """Inventory differences report."""
    desde, hasta = parse_date_range()
    diferencias = []
    productos = Producto.query.filter_by(activo=True).all()
    for p in productos:
        diarios = InventarioDiario.query.filter(
            InventarioDiario.producto_id == p.id,
            InventarioDiario.fecha >= desde,
            InventarioDiario.fecha <= hasta
        ).all()
        for d in diarios:
            esperado = calcular_stock_esperado(p.id, d.fecha)
            diff = float(d.cantidad_fisica) - esperado
            if abs(diff) > 0.01:
                diferencias.append({
                    'producto': p.nombre,
                    'fecha': d.fecha,
                    'esperado': round(esperado, 2),
                    'fisico': float(d.cantidad_fisica),
                    'diferencia': round(diff, 2)
                })

    diferencias.sort(key=lambda x: (x['fecha'], abs(x['diferencia'])), reverse=True)
    return render_template('reports/diferencias.html',
                           desde=desde, hasta=hasta,
                           diferencias=diferencias)


@reports_bp.route('/cierres', methods=['GET'])
@login_required
@encargado_required
def cierres():
    """Daily closes history."""
    desde, hasta = parse_date_range()
    cierres = CierreDiario.query.filter(
        CierreDiario.fecha >= desde,
        CierreDiario.fecha <= hasta
    ).order_by(CierreDiario.fecha.desc()).all()
    return render_template('reports/cierres.html',
                           desde=desde, hasta=hasta,
                           cierres=cierres)


@reports_bp.route('/movimientos/<int:producto_id>', methods=['GET'])
@login_required
@encargado_required
def movimientos(producto_id):
    """Detailed product movement history."""
    producto = Producto.query.get_or_404(producto_id)
    desde, hasta = parse_date_range()

    pedidos = db.session.query(PedidoDetalle).join(Pedido).filter(
        PedidoDetalle.producto_id == producto_id,
        Pedido.fecha >= desde,
        Pedido.fecha <= hasta
    ).order_by(Pedido.fecha.desc(), Pedido.hora.desc()).all()

    compras = db.session.query(CompraDetalle).join(Compra).filter(
        CompraDetalle.producto_id == producto_id,
        Compra.fecha >= desde,
        Compra.fecha <= hasta
    ).order_by(Compra.fecha.desc()).all()

    inventarios = InventarioDiario.query.filter(
        InventarioDiario.producto_id == producto_id,
        InventarioDiario.fecha >= desde,
        InventarioDiario.fecha <= hasta
    ).order_by(InventarioDiario.fecha.desc()).all()

    return render_template('reports/movimientos.html',
                           producto=producto, desde=desde, hasta=hasta,
                           pedidos=pedidos, compras=compras, inventarios=inventarios)