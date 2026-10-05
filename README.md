# 🍺 Gol de Oro — Sistema de Inventario SAAS

Sistema de facturación y control de inventario para la cantina de **Gol de Oro** (complejo de canchas de fútbol en Panamá).

**URL local:** http://localhost:8000

---

## 🚀 Stack

| Componente | Tecnología | Versión |
|---|---|---|
| Backend | **Python / Flask** | 3.11 / 3.1.* |
| ORM | **SQLAlchemy** | 3.1.* |
| Frontend | Jinja2 + TailwindCSS |
| DB | **PostgreSQL 16** (Docker) |
| Auth | Flask-Login 0.6.* + bcrypt 1.0.* |
| Migraciones | Flask-Migrate 4.1.* |
| Server | Gunicorn 23.* |
| Driver DB | psycopg2-binary 2.9.* |
| Email | Flask-Mail 0.9.* |

## 📁 Estructura

```
gol-de-oro/
├── app/                      # Aplicación Flask
│   ├── models/               # SQLAlchemy models
│   │   ├── user.py           # Usuario, roles
│   │   ├── product.py        # Productos
│   │   ├── order.py          # Pedidos
│   │   ├── inventory.py      # Inventario inicial/diario
│   │   ├── purchase.py       # Compras
│   │   ├── daily_close.py    # Cierre diario
│   │   ├── notification.py   # Notificaciones
│   │   ├── subscription.py   # Suscripciones
│   │   └── __init__.py
│   ├── routes/               # Blueprints
│   │   ├── auth.py           # Login/logout
│   │   ├── orders.py         # Gestión de pedidos
│   │   ├── inventory.py      # Control de inventario
│   │   ├── purchases.py      # Compras
│   │   ├── close.py          # Cierre diario
│   │   ├── reports.py        # Reportes
│   │   ├── admin.py          # Admin panel
│   │   ├── notifications.py  # Notificaciones
│   │   └── __init__.py
│   ├── services/             # Business logic
│   │   ├── order_service.py, inventory_service.py, close_service.py
│   │   ├── purchase_service.py, limits_service.py
│   │   ├── auth_service.py, email_service.py, backup_service.py
│   │   └── subscription_service.py
│   ├── utils/                # Decorators, helpers
│   │   ├── decorators.py, helpers.py, subscription_middleware.py
│   ├── templates/            # Jinja2 templates
│   ├── static/               # CSS, JS, images
│   └── config.py             # Config classes (dev/prod)
├── scripts/                  # Admin scripts
├── Dockerfile
├── docker-compose.yml
└── run.py
```

## ⚡ Inicio rápido

```bash
docker compose up -d
# Acceder: http://localhost:8000
```

## 🆕 Últimos cambios

- ✅ **MVP completo** — Ajustes UX: logo, aprobaciones, footer FDS, renombrado de ventas, cierre diario
- ✅ **Variables de entorno** — Credenciales DB eliminadas del código, usan `psycopg2` + env vars (`65e78d4`)
- ✅ **Seguridad** — Se removieron hardcoded DB credentials del código fuente
- ✅ **Arquitectura escalable** — Models, routes, services y utils separados por dominio
- ✅ **Docker** — PostgreSQL 16 Alpine + Flask con Gunicorn, healthcheck incluido

## 🧱 Modelos principales

- **Usuario** — Login, roles (admin/cajero)
- **Producto** — Catálogo con precios y stock
- **Pedido / PedidoDetalle** — Ventas con control de aprobación
- **Compra / CompraDetalle** — Reposición de inventario
- **InventarioInicial / InventarioDiario** — Control diario de existencias
- **CierreDiario** — Corte de caja
- **Notificación / Suscripcion** — Alertas de stock bajo y vencimientos

---

## 📋 Control de versiones

| Fecha | Commit | Descripción |
|---|---|---|
| 2026-10-05 | [`a6c4e85`](https://github.com/peter-cyber13/gol-de-oro/commit/a6c4e85) | Docs: README con stack actual, estructura y cambios recientes |
| 2026-09-25 | [`65e78d4`](https://github.com/peter-cyber13/gol-de-oro/commit/65e78d4) | Fix: remover credenciales DB hardcodeadas, usar env vars + psycopg2 |
| 2026-09-25 | [`956a806`](https://github.com/peter-cyber13/gol-de-oro/commit/956a806) | 🎯 MVP — ajustes UX: logo, aprobaciones, footer FDS, cierre diario |

---

**HEAD:** [`a6c4e85`](https://github.com/peter-cyber13/gol-de-oro/commit/a6c4e85) (2026-10-05)
**Inicio:** 2026-09-25 · **Última actualización:** 2026-10-05 | # commits: 3