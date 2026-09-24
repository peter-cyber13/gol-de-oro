"""Admin routes — user management, product management, SAAS, backup."""
from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import Usuario
from app.models.product import Producto
from app.models.subscription import Suscripcion
from app.models.daily_close import CierreDiario
from app.services.limits_service import verificar_limite_productos, get_usage_stats, LimiteAlcanzado
from app.services.subscription_service import get_subscription, registrar_pago
from app.services.backup_service import realizar_backup, restaurar_backup
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')


@admin_bp.route('')
@login_required
@admin_required
def panel():
    """Admin dashboard with usage stats."""
    stats = get_usage_stats()
    sub = get_subscription()
    return render_template('admin/panel.html', stats=stats, sub=sub)


# ── Users ──

@admin_bp.route('/usuarios', methods=['GET'])
@login_required
@admin_required
def usuarios():
    usuarios = Usuario.query.order_by(Usuario.fecha_creacion.desc()).all()
    stats = get_usage_stats()
    return render_template('admin/users.html', usuarios=usuarios, stats=stats)


@admin_bp.route('/usuarios/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_usuario():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        rol = request.form.get('rol', 'empleado')

        if not nombre or not email or not password:
            flash('Todos los campos son obligatorios.', 'error')
            return redirect(url_for('admin_bp.crear_usuario'))

        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'error')
            return redirect(url_for('admin_bp.crear_usuario'))

        if Usuario.query.filter_by(email=email).first():
            flash('Ya existe un usuario con ese correo.', 'error')
            return redirect(url_for('admin_bp.crear_usuario'))

        try:
            from app.services.auth_service import crear_usuario as create_user
            create_user(nombre=nombre, email=email, password=password, rol=rol)
            flash(f'Usuario {nombre} creado como {rol}.', 'success')
            return redirect(url_for('admin_bp.usuarios'))
        except LimiteAlcanzado as e:
            flash(str(e), 'error')
            return redirect(url_for('admin_bp.crear_usuario'))

    stats = get_usage_stats()
    return render_template('admin/user_form.html', stats=stats, usuario=None)


@admin_bp.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    if request.method == 'POST':
        usuario.nombre = request.form.get('nombre', '').strip()
        usuario.rol = request.form.get('rol', usuario.rol)
        activo = request.form.get('activo', '0') == '1'

        if id == current_user.id and not activo:
            flash('No puedes desactivar tu propia cuenta.', 'error')
            return redirect(url_for('admin_bp.editar_usuario', id=id))

        usuario.activo = activo

        password = request.form.get('password', '')
        if password:
            if len(password) < 6:
                flash('La contraseña debe tener al menos 6 caracteres.', 'error')
                return redirect(url_for('admin_bp.editar_usuario', id=id))
            usuario.set_password(password)

        db.session.commit()
        flash(f'Usuario {usuario.nombre} actualizado.', 'success')
        return redirect(url_for('admin_bp.usuarios'))

    stats = get_usage_stats()
    return render_template('admin/user_form.html', stats=stats, usuario=usuario)


# ── Products ──

@admin_bp.route('/productos', methods=['GET'])
@login_required
@admin_required
def productos():
    productos = Producto.query.order_by(Producto.activo.desc(), Producto.categoria, Producto.nombre).all()
    stats = get_usage_stats()
    return render_template('admin/products.html', productos=productos, stats=stats)


@admin_bp.route('/productos/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_producto():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        unidad = request.form.get('unidad_medida', 'unidad')
        categoria = request.form.get('categoria', 'otro')
        frecuencia = request.form.get('frecuencia_inventario', 'diario')

        if not nombre:
            flash('El nombre del producto es obligatorio.', 'error')
            return redirect(url_for('admin_bp.crear_producto'))

        if Producto.query.filter_by(nombre=nombre, activo=True).first():
            flash('Ya existe un producto con ese nombre.', 'error')
            return redirect(url_for('admin_bp.crear_producto'))

        try:
            verificar_limite_productos()
        except LimiteAlcanzado as e:
            flash(str(e), 'error')
            return redirect(url_for('admin_bp.crear_producto'))

        producto = Producto(nombre=nombre, unidad_medida=unidad, categoria=categoria, frecuencia_inventario=frecuencia)
        db.session.add(producto)
        db.session.commit()
        flash(f'Producto {nombre} creado.', 'success')
        return redirect(url_for('admin_bp.productos'))

    stats = get_usage_stats()
    return render_template('admin/product_form.html', stats=stats, producto=None)


@admin_bp.route('/productos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    if request.method == 'POST':
        producto.nombre = request.form.get('nombre', '').strip()
        producto.unidad_medida = request.form.get('unidad_medida', producto.unidad_medida)
        producto.categoria = request.form.get('categoria', producto.categoria)
        producto.frecuencia_inventario = request.form.get('frecuencia_inventario', producto.frecuencia_inventario)
        producto.activo = request.form.get('activo', '0') == '1'
        db.session.commit()
        flash(f'Producto {producto.nombre} actualizado.', 'success')
        return redirect(url_for('admin_bp.productos'))

    stats = get_usage_stats()
    return render_template('admin/product_form.html', stats=stats, producto=producto)


# ── Subscription ──

@admin_bp.route('/suscripcion', methods=['GET', 'POST'])
@login_required
@admin_required
def suscripcion():
    sub = get_subscription()
    if request.method == 'POST':
        action = request.form.get('action', '')
        if action == 'pagar':
            dias = int(request.form.get('dias', 30))
            registrar_pago(dias_extension=dias)
            flash(f'Pago registrado. Suscripción activa hasta {sub.fecha_vencimiento}.', 'success')
        return redirect(url_for('admin_bp.suscripcion'))

    return render_template('admin/subscriptions.html', sub=sub)


# ── Backup ──

@admin_bp.route('/backup', methods=['GET', 'POST'])
@login_required
@admin_required
def backup():
    if request.method == 'POST':
        action = request.form.get('action', '')
        if action == 'crear':
            try:
                path = realizar_backup()
                flash(f'Backup creado: {path}', 'success')
            except RuntimeError as e:
                flash(f'Error: {e}', 'error')
        elif action == 'restaurar':
            from flask import request as req
            archivo = req.form.get('archivo', '')
            if archivo:
                try:
                    restaurar_backup(archivo)
                    flash('Base de datos restaurada.', 'success')
                except (RuntimeError, FileNotFoundError) as e:
                    flash(f'Error: {e}', 'error')
        return redirect(url_for('admin_bp.backup'))

    return render_template('admin/backups.html')


# ── Notifications ──

@admin_bp.route('/notificaciones', methods=['GET'])
@login_required
@admin_required
def notificaciones():
    return redirect(url_for('notifications_bp.listar'))