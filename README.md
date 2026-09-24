# 🍺 Gol de Oro — Sistema de Inventario SAAS

Sistema de facturación de producto y control de inventario para la cantina de Gol de Oro (complejo de canchas de fútbol).

## MVP Local

```bash
docker compose up -d
# Acceder: http://localhost:8000
```

## Stack

- **Backend:** Python / Flask + SQLAlchemy
- **Frontend:** Jinja2 + TailwindCSS
- **DB:** PostgreSQL 16 (Docker)
- **Auth:** Flask-Login + bcrypt
- **Server:** Gunicorn

## Estructura

```
gol-de-oro/
├── app/            # Aplicación Flask
│   ├── models/     # SQLAlchemy models
│   ├── routes/     # Blueprints
│   ├── services/   # Business logic
│   ├── templates/  # Jinja2 templates
│   ├── static/     # CSS, JS, images
│   └── utils/      # Decorators, helpers
├── scripts/        # Admin scripts
├── Dockerfile
├── docker-compose.yml
└── run.py
```