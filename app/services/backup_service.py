"""Backup service — pg_dump/pg_restore."""
import subprocess
import os
from datetime import datetime
from flask import current_app


def get_db_url():
    """Get DATABASE_URL from config."""
    return current_app.config['SQLALCHEMY_DATABASE_URI']


def realizar_backup(destino=None):
    """Execute pg_dump to a file. Returns path to backup file."""
    if not destino:
        os.makedirs('backups', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        destino = f"backups/goldeoro_{timestamp}.sql"

    db_url = get_db_url()

    cmd = [
        'pg_dump',
        '--no-owner',
        '--no-acl',
        '-f', destino,
        db_url
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(f"pg_dump failed: {result.stderr}")
        return destino
    except FileNotFoundError:
        raise RuntimeError("pg_dump no encontrado. Instala postgresql-client.")
    except subprocess.TimeoutExpired:
        raise RuntimeError("pg_dump timed out after 120s.")


def restaurar_backup(origen):
    """Restore from a pg_dump file."""
    if not os.path.exists(origen):
        raise FileNotFoundError(f"Backup file not found: {origen}")

    db_url = get_db_url()

    cmd = [
        'psql',
        '-f', origen,
        db_url
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"Restore failed: {result.stderr}")
        return True
    except FileNotFoundError:
        raise RuntimeError("psql no encontrado. Instala postgresql-client.")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Restore timed out after 300s.")