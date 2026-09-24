"""Close service — daily closing logic."""
import json
from datetime import date
from app.extensions import db
from app.models.daily_close import CierreDiario
from app.models.inventory import InventarioDiario
from app.models.product import Producto
from app.services.inventory_service import verificar_diferencia


def hay_inventario_cargado(fecha):
    """Check if all active (diario-frequency) products have inventory for this date."""
    productos = Producto.query.filter_by(activo=True).count()
    if productos == 0:
        return False
    inventariados = InventarioDiario.query.filter_by(fecha=fecha).count()
    return inventariados >= productos


def hay_cierre(fecha):
    """Check if a close already exists for this date."""
    return CierreDiario.query.filter_by(fecha=fecha).first() is not None


def realizar_cierre(usuario_id, fecha=None):
    """
    Execute daily close: compare physical vs expected for all products.
    Returns the CierreDiario object.
    """
    if fecha is None:
        fecha = date.today()

    if not hay_inventario_cargado(fecha):
        raise ValueError("El inventario del día no está completo. Carga todos los productos primero.")

    if hay_cierre(fecha):
        raise ValueError(f"Ya existe un cierre para el día {fecha}")

    productos = Producto.query.filter_by(activo=True).all()
    diferencias = []
    correctos = 0
    con_diferencia = 0

    for p in productos:
        dif = verificar_diferencia(p.id, fecha)
        if dif is None:
            continue
        if dif['diferencia'] == 0:
            correctos += 1
        else:
            con_diferencia += 1
            diferencias.append({
                'producto_id': p.id,
                'producto': p.nombre,
                'esperado': dif['esperado'],
                'fisico': dif['fisico'],
                'diferencia': dif['diferencia']
            })

    cierre = CierreDiario(
        fecha=fecha,
        usuario_encargado_id=usuario_id,
        productos_correctos=correctos,
        productos_con_diferencia=con_diferencia,
        diferencia_detectada=json.dumps(diferencias, default=str),
        notificado_app=True
    )
    db.session.add(cierre)
    db.session.commit()

    # Create notification for encargado
    from app.models.notification import Notificacion
    total_prods = correctos + con_diferencia
    noti = Notificacion(
        usuario_id=usuario_id,
        tipo='cierre_realizado',
        mensaje=f"Cierre del {fecha} completado: {correctos}/{total_prods} productos correctos"
    )
    db.session.add(noti)
    db.session.commit()

    return cierre


def obtener_resumen_cierre(fecha=None):
    """Get closing summary for display."""
    if fecha is None:
        fecha = date.today()

    cierre = CierreDiario.query.filter_by(fecha=fecha).first()

    from app.models.order import Pedido
    total_pedidos = Pedido.query.filter(Pedido.fecha == fecha).count()

    from app.models.inventory import InventarioDiario
    total_inventariado = InventarioDiario.query.filter_by(fecha=fecha).count()

    total_productos = Producto.query.filter_by(activo=True).count()

    return {
        'cierre': cierre,
        'total_pedidos': total_pedidos,
        'total_inventariado': total_inventariado,
        'total_productos': total_productos,
        'productos_pendientes': total_productos - total_inventariado
    }