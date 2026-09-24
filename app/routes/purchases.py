"""Purchases routes — register supplier purchases."""
from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.product import Producto
from app.services.purchase_service import crear_compra, obtener_compras
from app.utils.decorators import encargado_required

purchases_bp = Blueprint('purchases_bp', __name__, url_prefix='/compras')


@purchases_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
@encargado_required
def nueva():
    """Register a new purchase from supplier."""
    if request.method == 'POST':
        proveedor = request.form.get('proveedor', '')
        folio_compra = request.form.get('folio_compra', '')
        fecha_str = request.form.get('fecha', '')

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else date.today()
        except ValueError:
            flash('Fecha inválida.', 'error')
            return redirect(url_for('purchases_bp.nueva'))

        producto_ids = request.form.getlist('producto_id[]')
        cantidades = request.form.getlist('cantidad[]')

        productos = []
        for pid, qty in zip(producto_ids, cantidades):
            if qty and float(qty) > 0:
                productos.append({'id': int(pid), 'cantidad': float(qty)})

        if not productos:
            flash('Agrega al menos un producto con cantidad.', 'error')
            return redirect(url_for('purchases_bp.nueva'))

        try:
            compra = crear_compra(
                usuario_id=current_user.id,
                fecha=fecha,
                proveedor=proveedor,
                folio_compra=folio_compra,
                productos=productos
            )
            flash(f'✅ Compra registrada: {compra.proveedor or "Sin proveedor"}', 'success')
            return redirect(url_for('purchases_bp.listar'))

        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('purchases_bp.nueva'))

    # GET
    productos = Producto.query.filter_by(activo=True).order_by(
        Producto.categoria, Producto.nombre
    ).all()

    return render_template('purchases/new.html', productos=productos, today=date.today())


@purchases_bp.route('', methods=['GET'])
@login_required
@encargado_required
def listar():
    """List purchases with optional date range."""
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

    compras = obtener_compras(fecha_desde=desde, fecha_hasta=hasta)
    return render_template('purchases/list.html', compras=compras, desde=desde, hasta=hasta)