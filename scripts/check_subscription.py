"""Daily SAAS check — run via cron."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.services.subscription_service import verificar_vencimiento


def check():
    app = create_app()
    with app.app_context():
        result = verificar_vencimiento()
        if result['aviso']:
            print('[SAAS] Aviso: suscripción vence en menos de 7 días')
        if result['suspendida']:
            print('[SAAS] Suscripción suspendida por vencimiento')
        if not result['aviso'] and not result['suspendida']:
            print('[SAAS] Suscripción al día')


if __name__ == '__main__':
    check()