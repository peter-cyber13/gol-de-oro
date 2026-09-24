"""Notifications routes."""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.notification import Notificacion

notifications_bp = Blueprint('notifications_bp', __name__, url_prefix='/notificaciones')


@notifications_bp.route('', methods=['GET'])
@login_required
def listar():
    notificaciones = Notificacion.query.filter_by(
        usuario_id=current_user.id
    ).order_by(Notificacion.fecha_creacion.desc()).limit(50).all()
    no_leidas = Notificacion.query.filter_by(
        usuario_id=current_user.id, leida=False
    ).count()
    return render_template('notifications/list.html',
                           notificaciones=notificaciones,
                           no_leidas=no_leidas)


@notifications_bp.route('/<int:id>/leer', methods=['POST'])
@login_required
def marcar_leida(id):
    noti = Notificacion.query.get_or_404(id)
    if noti.usuario_id != current_user.id:
        flash('No tienes permiso para ver esta notificación.', 'error')
        return redirect(url_for('notifications_bp.listar'))
    noti.leida = True
    db.session.commit()
    return redirect(url_for('notifications_bp.listar'))