"""Auth routes — login, logout, password recovery."""
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import Usuario
from app.services.auth_service import autenticar, iniciar_recuperacion, completar_recuperacion
from app.services.email_service import enviar_recuperacion

auth_bp = Blueprint('auth_bp', __name__, url_prefix='')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        usuario = autenticar(email, password)
        if usuario:
            login_user(usuario)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Correo o contraseña incorrectos', 'error')
        return render_template('login.html')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_bp.login'))


@auth_bp.route('/recuperar', methods=['GET', 'POST'])
def recover_form():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        token = iniciar_recuperacion(email)
        if token:
            enviar_recuperacion(email, token)
        # Always show same message (don't reveal if email exists)
        flash('Si el correo está registrado, recibirás instrucciones para recuperar tu contraseña.', 'info')
        return render_template('recover.html')

    return render_template('recover.html')


@auth_bp.route('/recuperar/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        if not password or len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'error')
            return render_template('reset_password.html', token=token)

        if password != confirm:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('reset_password.html', token=token)

        usuario = completar_recuperacion(token, password)
        if usuario:
            flash('Contraseña actualizada. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('auth_bp.login'))
        else:
            flash('El enlace de recuperación es inválido o ha expirado.', 'error')
            return redirect(url_for('auth_bp.recover_form'))

    return render_template('reset_password.html', token=token)


# API endpoints for HTMX/JS
@auth_bp.route('/api/enviar-recuperacion', methods=['POST'])
def api_recuperar():
    email = request.json.get('email', '').strip().lower()
    token = iniciar_recuperacion(email)
    if token:
        enviar_recuperacion(email, token)
    return jsonify({'message': 'Si el correo está registrado, recibirás instrucciones.'}), 200


@auth_bp.route('/api/cambiar-pass', methods=['POST'])
def api_cambiar_pass():
    data = request.json or {}
    token = data.get('token', '')
    password = data.get('password', '')
    if not password or len(password) < 6:
        return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres.'}), 400
    usuario = completar_recuperacion(token, password)
    if not usuario:
        return jsonify({'error': 'Token inválido o expirado.'}), 400
    return jsonify({'message': 'Contraseña actualizada.'}), 200