"""Orders routes — new pedido (★ heart of the system) + list + detail."""
import json
from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.order import Pedido, PedidoDetalle, SolicitudModificacion
from app.models.product import Producto
from app.models.user import Usuario
from app.services.order_service import crear_pedido, obtener_pedidos
from app.utils.decorators import empleado_required, encargado_required

orders_bp = Blueprint('orders_bp', __name__, url_prefix='/pedidos')


@orders_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@empleado_required
def nuevo():
    """New pedido — core functionality."""
    if request.method == 'POST':
        if request.is_json:
            data = request.json
        else:
            data = request.form

        cliente = data.get('cliente', '')
        productos_raw = data.get('productos', '')

        if request.is_json:
            productos = data.get('productos', [])
        else:
            import json
            try:
                productos = json.loads(productos_raw) if productos_raw else []
            except json.JSONDecodeError:
                flash('Error en el formato de productos.', 'error')
                return redirect(url_for('orders_bp.nuevo'))

        if not productos:
            flash('Agrega al menos un producto.', 'error')
            return redirect(url_for('orders_bp.nuevo'))

        try:
            pedido = crear_pedido(
                usuario_id=current_user.id,
                fecha=date.today(),
                cliente=cliente,
                productos=productos
            )
            if request.is_json:
                return jsonify({
                    'success': True,
                    'folio': pedido.folio,
                    'message': f'✅ Pedido {pedido.folio} registrado'
                }), 200
            flash(f'✅ Pedido {pedido.folio} registrado', 'success')
            return redirect(url_for('orders_bp.nuevo'))

        except ValueError as e:
            if request.is_json:
                return jsonify({'success': False, 'error': str(e)}), 400
            flash(str(e), 'error')
            return redirect(url_for('orders_bp.nuevo'))

    # GET — show the form
    categorias = Producto.query.filter_by(activo=True).with_entities(
        Producto.categoria
    ).distinct().all()
    categorias = [c[0] for c in categorias]

    productos = Producto.query.filter_by(activo=True).order_by(
        Producto.categoria, Producto.nombre
    ).all()

    return render_template('orders/new.html',
                           categorias=categorias,
                           productos=productos)


@orders_bp.route('', methods=['GET'])
@login_required
def listar():
    """List pedidos, optionally filtered by date."""
    fecha_str = request.args.get('fecha', '')
    fecha = None
    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    if not fecha:
        fecha = date.today()

    pedidos = obtener_pedidos(fecha=fecha)
    return render_template('orders/list.html', pedidos=pedidos, fecha=fecha)


@orders_bp.route('/<int:id>', methods=['GET'])
@login_required
def detalle(id):
    pedido = Pedido.query.get_or_404(id)
    es_vendedor = current_user.rol in ('admin', 'encargado', 'empleado')
    es_encargado = current_user.rol in ('admin', 'encargado')
    # Solicitudes pendientes para que el encargado apruebe/rechace este pedido
    solicitudes_pendientes = []
    if es_encargado:
        solicitudes_pendientes = SolicitudModificacion.query.filter_by(
            pedido_id=id, estado='pendiente'
        ).all()
    return render_template(
        'orders/detail.html',
        pedido=pedido,
        es_vendedor=es_vendedor,
        es_encargado=es_encargado,
        solicitudes_pendientes=solicitudes_pendientes,
        productos=Producto.query.filter_by(activo=True).order_by(Producto.nombre).all(),
    )


@orders_bp.route('/<int:id>/editar', methods=['POST'])
@login_required
@empleado_required
def solicitar_edicion(id):
    """Vendedor envía productos modificados → crea solicitud pendiente (no modifica el pedido)."""
    pedido = Pedido.query.get_or_404(id)
    data = request.get_json(silent=True) or request.form
    productos_raw = data.get('productos', [])

    if isinstance(productos_raw, str):
        try:
            productos = json.loads(productos_raw) if productos_raw else []
        except json.JSONDecodeError:
            return jsonify({'success': False, 'error': 'Formato de productos inválido.'}), 400
    else:
        productos = productos_raw

    if not productos:
        return jsonify({'success': False, 'error': 'Agrega al menos un producto.'}), 400

    # Validar productos
    for item in productos:
        prod = Producto.query.get(item.get('id'))
        if not prod or not prod.activo:
            return jsonify({'success': False, 'error': 'Producto inválido.'}), 400
        try:
            cantidad = float(item.get('cantidad'))
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'Cantidad inválida.'}), 400
        if cantidad <= 0:
            return jsonify({'success': False, 'error': 'La cantidad debe ser mayor a 0.'}), 400

    solicitud = SolicitudModificacion(
        pedido_id=pedido.id,
        usuario_solicita_id=current_user.id,
        productos_json=json.dumps(productos, ensure_ascii=False),
        estado='pendiente',
    )
    db.session.add(solicitud)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '✅ Solicitud de modificación enviada. Espera aprobación del encargado.'
    }), 200


# API endpoint for product search (used by orders.js)
@orders_bp.route('/api/productos-disponibles', methods=['GET'])
@login_required
def api_productos():
    categoria = request.args.get('categoria', '')
    q = request.args.get('q', '')

    query = Producto.query.filter_by(activo=True)
    if categoria:
        query = query.filter_by(categoria=categoria)
    if q:
        query = query.filter(Producto.nombre.ilike(f'%{q}%'))

    productos = query.order_by(Producto.nombre).all()
    return jsonify([{
        'id': p.id,
        'nombre': p.nombre,
        'categoria': p.categoria,
        'unidad_medida': p.unidad_medida,
    } for p in productos])


# ─── Aprobaciones de modificaciones ────────────────────────────────

@orders_bp.route('/<int:id>/solicitudes', methods=['GET'])
@login_required
def api_solicitudes_pedido(id):
    """Devuelve las solicitudes pendientes de un pedido (para el modal)."""
    Pedido.query.get_or_404(id)
    solicitudes = SolicitudModificacion.query.filter_by(pedido_id=id, estado='pendiente').all()
    data = []
    for s in solicitudes:
        data.append({
            'id': s.id,
            'productos': json.loads(s.productos_json),
            'solicitante': s.solicitante.nombre if s.solicitante else '—',
            'fecha_solicitud': s.fecha_solicitud.strftime('%Y-%m-%d %H:%M') if s.fecha_solicitud else '',
        })
    return jsonify(data)


# ─── Ruta global de aprobaciones ───────────────────────────────────

from flask import Blueprint as _Blueprint

aprobaciones_bp = _Blueprint('aprobaciones_bp', __name__, url_prefix='/aprobaciones')


@aprobaciones_bp.route('', methods=['GET'])
@login_required
@encargado_required
def listar():
    """Lista todas las solicitudes de modificación pendientes."""
    solicitudes = SolicitudModificacion.query.filter_by(estado='pendiente').order_by(
        SolicitudModificacion.fecha_solicitud.desc()
    ).all()
    productos = Producto.query.filter_by(activo=True).order_by(Producto.nombre).all()
    return render_template('approvals/list.html', solicitudes=solicitudes, productos=productos)


@aprobaciones_bp.route('/<int:id>/aprobar', methods=['POST'])
@login_required
@encargado_required
def aprobar(id):
    """Aprueba la solicitud: reemplaza los detalles del pedido original con los nuevos."""
    solicitud = SolicitudModificacion.query.get_or_404(id)
    if solicitud.estado != 'pendiente':
        flash('Esta solicitud ya fue procesada.', 'error')
        return redirect(url_for('aprobaciones_bp.listar'))

    pedido = solicitud.pedido
    nuevos_productos = json.loads(solicitud.productos_json)

    # Reemplazar detalles
    PedidoDetalle.query.filter_by(pedido_id=pedido.id).delete()
    for item in nuevos_productos:
        detalle = PedidoDetalle(
            pedido_id=pedido.id,
            producto_id=item['id'],
            cantidad=item['cantidad'],
        )
        db.session.add(detalle)

    # Marcar solicitud
    solicitud.estado = 'aprobado'
    solicitud.usuario_aprueba_id = current_user.id
    solicitud.fecha_respuesta = datetime.utcnow()

    db.session.commit()
    flash(f'✅ Solicitud de modificación aprobada para pedido {pedido.folio}.', 'success')
    return redirect(url_for('aprobaciones_bp.listar'))


@aprobaciones_bp.route('/<int:id>/rechazar', methods=['POST'])
@login_required
@encargado_required
def rechazar(id):
    """Rechaza la solicitud de modificación."""
    solicitud = SolicitudModificacion.query.get_or_404(id)
    if solicitud.estado != 'pendiente':
        flash('Esta solicitud ya fue procesada.', 'error')
        return redirect(url_for('aprobaciones_bp.listar'))

    solicitud.estado = 'rechazado'
    solicitud.usuario_aprueba_id = current_user.id
    solicitud.fecha_respuesta = datetime.utcnow()

    db.session.commit()
    flash(f'❌ Solicitud de modificación rechazada para pedido {solicitud.pedido.folio}.', 'error')
    return redirect(url_for('aprobaciones_bp.listar'))