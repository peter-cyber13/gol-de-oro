"""Inventory routes — carga inicial + inventario diario."""
from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.inventory import InventarioInicial, InventarioDiario
from app.models.product import Producto
from app.services.inventory_service import verificar_diferencia, calcular_stock_esperado
from app.utils.decorators import empleado_required, encargado_required

inventory_bp = Blueprint('inventory_bp', __name__, url_prefix='/inventario')


@inventory_bp.route('/inicial', methods=['GET', 'POST'])
@login_required
@encargado_required
def inicial():
    """Carga inicial de inventario (one-time per product)."""
    if request.method == 'POST':
        producto_id = request.form.get('producto_id', type=int)
        cantidad = request.form.get('cantidad', type=float)

        if not producto_id or cantidad is None:
            flash('Selecciona un producto y especifica una cantidad.', 'error')
            return redirect(url_for('inventory_bp.inicial'))

        # Check if already has initial inventory
        existe = InventarioInicial.query.filter_by(producto_id=producto_id).first()
        if existe:
            flash('Este producto ya tiene inventario inicial registrado.', 'warning')
            return redirect(url_for('inventory_bp.inicial'))

        inv = InventarioInicial(
            producto_id=producto_id,
            cantidad=cantidad,
            usuario_id=current_user.id
        )
        db.session.add(inv)
        db.session.commit()
        flash(f'Inventario inicial registrado para {inv.producto.nombre}.', 'success')
        return redirect(url_for('inventory_bp.inicial'))

    productos_sin_inicial = Producto.query.filter(
        Producto.activo == True,
        ~Producto.id.in_(
            db.session.query(InventarioInicial.producto_id)
        )
    ).all()

    productos_con_inicial = db.session.query(Producto).join(
        InventarioInicial, Producto.id == InventarioInicial.producto_id
    ).filter(Producto.activo == True).all()

    return render_template('inventory/initial.html',
                           productos_sin_inicial=productos_sin_inicial,
                           productos_con_inicial=productos_con_inicial)


@inventory_bp.route('/diario', methods=['GET', 'POST'])
@login_required
@empleado_required
def diario():
    """Inventario diario — conteo físico de productos."""
    fecha_str = request.args.get('fecha', '')
    fecha = date.today()
    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    if request.method == 'POST':
        producto_id = request.form.get('producto_id', type=int)
        cantidad = request.form.get('cantidad_fisica', type=float)

        if not producto_id or cantidad is None:
            flash('Selecciona un producto e ingresa la cantidad física.', 'error')
            return redirect(url_for('inventory_bp.diario', fecha=fecha))

        # Upsert
        existente = InventarioDiario.query.filter_by(
            producto_id=producto_id, fecha=fecha
        ).first()

        if existente:
            existente.cantidad_fisica = cantidad
            existente.usuario_id = current_user.id
            existente.fecha_registro = datetime.utcnow()
        else:
            inv = InventarioDiario(
                producto_id=producto_id,
                cantidad_fisica=cantidad,
                fecha=fecha,
                usuario_id=current_user.id
            )
            db.session.add(inv)

        db.session.commit()
        flash('Inventario actualizado.', 'success')
        return redirect(url_for('inventory_bp.diario', fecha=fecha))

    # GET
    productos = Producto.query.filter_by(activo=True).order_by(
        Producto.categoria, Producto.nombre
    ).all()

    inventario_data = []
    for p in productos:
        diario = InventarioDiario.query.filter_by(
            producto_id=p.id, fecha=fecha
        ).first()
        esperado = calcular_stock_esperado(p.id, fecha)
        inventario_data.append({
            'producto': p,
            'diario': diario,
            'esperado': round(esperado, 2),
            'diferencia': round(float(diario.cantidad_fisica) - esperado, 2) if diario else None
        })

    total_productos = len(productos)
    inventariados = sum(1 for d in inventario_data if d['diario'] is not None)

    return render_template('inventory/daily.html',
                           fecha=fecha,
                           inventario_data=inventario_data,
                           total_productos=total_productos,
                           inventariados=inventariados)


@inventory_bp.route('/diario/<fecha>', methods=['GET'])
@login_required
@encargado_required
def diario_por_fecha(fecha):
    """View daily inventory for a specific date (encargado/admin only)."""
    try:
        fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
    except ValueError:
        flash('Fecha inválida.', 'error')
        return redirect(url_for('inventory_bp.diario'))
    return redirect(url_for('inventory_bp.diario', fecha=fecha))