"""Close routes — daily closing."""
from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.product import Producto
from app.services.close_service import (
    realizar_cierre, hay_cierre, hay_inventario_cargado, obtener_resumen_cierre
)
from app.utils.decorators import encargado_required

close_bp = Blueprint('close_bp', __name__, url_prefix='/cierre')


@close_bp.route('', methods=['GET', 'POST'])
@login_required
@encargado_required
def cierre():
    """Daily close management."""
    fecha_str = request.args.get('fecha', '')
    fecha = date.today()
    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    if request.method == 'POST':
        action = request.form.get('action', '')

        if action == 'realizar':
            try:
                cierre = realizar_cierre(
                    usuario_id=current_user.id,
                    fecha=fecha
                )
                flash(f'✅ Cierre del {fecha} completado. {cierre.productos_correctos} productos OK.', 'success')
                return redirect(url_for('close_bp.cierre', fecha=fecha))
            except ValueError as e:
                flash(str(e), 'error')
                return redirect(url_for('close_bp.cierre', fecha=fecha))

    resumen = obtener_resumen_cierre(fecha)
    tiene_cierre = hay_cierre(fecha)
    inventario_completo = hay_inventario_cargado(fecha)

    return render_template('close/daily.html',
                           fecha=fecha,
                           resumen=resumen,
                           tiene_cierre=tiene_cierre,
                           inventario_completo=inventario_completo)