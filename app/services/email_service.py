"""Email service — SMTP for password recovery."""
from flask import current_app, render_template
from app.extensions import mail as mail_ext
from flask_mail import Message


def enviar_email(destinatario, asunto, cuerpo_html):
    """Send an email. Silently fails if mail is not configured."""
    try:
        msg = Message(
            subject=asunto,
            recipients=[destinatario],
            html=cuerpo_html,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        mail_ext.send(msg)
        return True
    except Exception as e:
        current_app.logger.warning(f"Error enviando email a {destinatario}: {e}")
        return False


def enviar_recuperacion(email, token):
    """Send password recovery email with reset link."""
    base_url = 'http://localhost:8000'
    reset_url = f"{base_url}/recuperar/{token}"

    cuerpo_html = f"""
    <h2>Recuperación de contraseña — Gol de Oro</h2>
    <p>Has solicitado recuperar tu contraseña. Haz clic en el siguiente enlace para crear una nueva:</p>
    <p><a href="{reset_url}" style="background:#d4a843;color:#fff;padding:10px 20px;text-decoration:none;border-radius:5px;">
        Restablecer contraseña
    </a></p>
    <p>Este enlace expira en 1 hora.</p>
    <p>Si no solicitaste esto, ignora este mensaje.</p>
    <hr>
    <p style="color:#6b7280;font-size:12px;">Sistema de Inventario Gol de Oro</p>
    """

    return enviar_email(
        destinatario=email,
        asunto="Recuperación de contraseña — Gol de Oro",
        cuerpo_html=cuerpo_html
    )