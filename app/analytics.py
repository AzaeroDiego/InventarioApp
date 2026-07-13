from datetime import datetime

from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func, desc

from app import db
from app.models import Producto, Categoria, MovimientoStock, AlertaStock, Venta, Lote


analytics_bp = Blueprint('analytics', __name__)


def _costo_promedio_por_producto():
    """Devuelve costo promedio unitario por nombre de producto final usando lotes preparados."""
    costos = {}
    lotes_costos = db.session.query(
        Lote.nombre,
        func.sum(Lote.costo_total).label('costo_total'),
        func.sum(Lote.cantidad_preparada).label('cantidad_total')
    ).group_by(Lote.nombre).all()

    for nombre, costo_total, cantidad_total in lotes_costos:
        if cantidad_total and cantidad_total > 0:
            costos[nombre] = float(costo_total or 0) / float(cantidad_total)

    return costos


def _resumen_ventas_por_fecha(fecha_objetivo):
    """Calcula ventas, utilidad estimada y desglose por producto para una fecha."""
    if not fecha_objetivo:
        return {
            'ventas': [],
            'cantidad_operaciones': 0,
            'total_vendido': 0,
            'utilidad_estimada': 0,
            'costo_estimado': 0,
            'margen_estimado': 0,
            'productos': []
        }

    ventas = Venta.query.join(Producto).filter(
        func.date(Venta.fecha) == fecha_objetivo,
        Producto.activo == True,
        Producto.se_vende == True
    ).order_by(desc(Venta.fecha)).all()

    costos_por_producto = _costo_promedio_por_producto()
    total_vendido = 0
    costo_estimado = 0
    utilidad_estimada = 0
    productos = {}

    for venta in ventas:
        producto = venta.producto
        costo_unitario = costos_por_producto.get(producto.nombre, 0)
        costo_venta = float(venta.cantidad or 0) * costo_unitario
        utilidad_venta = float(venta.total or 0) - costo_venta

        total_vendido += float(venta.total or 0)
        costo_estimado += costo_venta
        utilidad_estimada += utilidad_venta

        if producto.nombre not in productos:
            productos[producto.nombre] = {
                'nombre': producto.nombre,
                'cantidad': 0,
                'total': 0,
                'costo': 0,
                'utilidad': 0,
                'costo_unitario': costo_unitario
            }

        productos[producto.nombre]['cantidad'] += venta.cantidad or 0
        productos[producto.nombre]['total'] += float(venta.total or 0)
        productos[producto.nombre]['costo'] += costo_venta
        productos[producto.nombre]['utilidad'] += utilidad_venta

    margen_estimado = (utilidad_estimada / total_vendido * 100) if total_vendido else 0

    return {
        'ventas': ventas,
        'cantidad_operaciones': len(ventas),
        'total_vendido': total_vendido,
        'utilidad_estimada': utilidad_estimada,
        'costo_estimado': costo_estimado,
        'margen_estimado': margen_estimado,
        'productos': sorted(productos.values(), key=lambda x: x['total'], reverse=True)
    }


def _primer_dia_mes(fecha):
    return datetime(fecha.year, fecha.month, 1)


def _sumar_meses(fecha, meses):
    mes_base = fecha.month - 1 + meses
    year = fecha.year + mes_base // 12
    month = mes_base % 12 + 1
    return datetime(year, month, 1)


def _meses_ultimos_6(fecha_referencia=None):
    """Genera 6 meses cerrando en el mes de referencia para evitar huecos cuando crezca la data."""
    if fecha_referencia is None:
        fecha_referencia = datetime.utcnow()

    fin = _primer_dia_mes(fecha_referencia)
    inicio = _sumar_meses(fin, -5)

    meses = []
    actual = inicio
    while actual <= fin:
        meses.append({
            'key': actual.strftime('%Y-%m'),
            'label': actual.strftime('%m/%Y'),
            'fecha': actual
        })
        actual = _sumar_meses(actual, 1)

    return meses, inicio


def _resumen_mensual_6_meses():
    """Ventas, utilidad y gasto de ingreso de stock de los últimos 6 meses."""
    ultima_venta = db.session.query(func.max(Venta.fecha)).scalar()
    ultimo_movimiento = db.session.query(func.max(MovimientoStock.fecha)).scalar()
    fecha_referencia = ultima_venta or ultimo_movimiento or datetime.utcnow()

    meses, fecha_inicio = _meses_ultimos_6(fecha_referencia)
    resumen = {
        mes['key']: {
            'mes': mes['label'],
            'ventas': 0,
            'costo_ventas': 0,
            'utilidad': 0,
            'margen': 0,
            'gasto_stock': 0
        }
        for mes in meses
    }

    costos_por_producto = _costo_promedio_por_producto()

    ventas = Venta.query.join(Producto).filter(
        Venta.fecha >= fecha_inicio,
        Producto.activo == True,
        Producto.se_vende == True
    ).all()

    for venta in ventas:
        producto = venta.producto
        key = venta.fecha.strftime('%Y-%m')
        if key not in resumen:
            continue

        total = float(venta.total or 0)
        costo_unitario = costos_por_producto.get(producto.nombre, 0)
        costo_venta = float(venta.cantidad or 0) * costo_unitario

        resumen[key]['ventas'] += total
        resumen[key]['costo_ventas'] += costo_venta
        resumen[key]['utilidad'] += total - costo_venta

    entradas_stock = db.session.query(MovimientoStock, Producto).join(
        Producto, Producto.id == MovimientoStock.producto_id
    ).filter(
        MovimientoStock.tipo == 'entrada',
        MovimientoStock.fecha >= fecha_inicio
    ).all()

    motivos_no_compra = {
        'Preparación de lote',
        'Reversión por eliminación de venta',
        'Reversión por eliminación de lote'
    }

    for movimiento, producto in entradas_stock:
        if movimiento.motivo in motivos_no_compra:
            continue

        key = movimiento.fecha.strftime('%Y-%m')
        if key not in resumen:
            continue

        resumen[key]['gasto_stock'] += float(movimiento.cantidad or 0) * float(producto.precio or 0)

    for datos in resumen.values():
        datos['margen'] = (datos['utilidad'] / datos['ventas'] * 100) if datos['ventas'] else 0

    return list(resumen.values())


@analytics_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard con ventas del último día registrado y utilidad estimada."""
    total_productos = Producto.query.filter_by(activo=True).count()

    productos_bajo_stock = Producto.query.filter(
        (Producto.activo == True) & (Producto.cantidad_stock < Producto.stock_minimo)
    ).all()

    valor_total = db.session.query(
        func.sum(Producto.precio * Producto.cantidad_stock)
    ).filter(Producto.activo == True).scalar() or 0

    movimientos_recientes = MovimientoStock.query.order_by(
        desc(MovimientoStock.fecha)
    ).limit(10).all()

    alertas_no_leidas = AlertaStock.query.filter_by(leida=False).count()

    ultima_fecha_venta = db.session.query(func.max(func.date(Venta.fecha))).scalar()
    resumen_ultima_fecha = _resumen_ventas_por_fecha(ultima_fecha_venta)

    return render_template(
        'main/dashboard.html',
        total_productos=total_productos,
        productos_bajo_stock=productos_bajo_stock,
        valor_total=valor_total,
        movimientos_recientes=movimientos_recientes,
        alertas_no_leidas=alertas_no_leidas,
        entradas_recientes=0,
        salidas_recientes=0,
        ventas_hoy=resumen_ultima_fecha['ventas'],
        total_ventas_hoy=resumen_ultima_fecha['total_vendido'],
        ultima_fecha_venta=ultima_fecha_venta,
        cantidad_ventas_ultima_fecha=resumen_ultima_fecha['cantidad_operaciones'],
        total_ventas_ultima_fecha=resumen_ultima_fecha['total_vendido'],
        costo_ventas_ultima_fecha=resumen_ultima_fecha['costo_estimado'],
        utilidad_ultima_fecha=resumen_ultima_fecha['utilidad_estimada'],
        margen_ultima_fecha=resumen_ultima_fecha['margen_estimado'],
        productos_ultima_fecha=resumen_ultima_fecha['productos']
    )


@analytics_bp.route('/reportes')
@login_required
def reportes():
    """Reportes basados en ventas reales de productos finales."""
    productos_vendidos = db.session.query(
        Producto.nombre,
        func.sum(Venta.cantidad).label('total')
    ).join(Venta, Venta.producto_id == Producto.id).filter(
        Producto.activo == True,
        Producto.se_vende == True
    ).group_by(Producto.id, Producto.nombre).order_by(desc('total')).limit(10).all()

    valor_por_categoria = db.session.query(
        Categoria.nombre,
        func.sum(Producto.precio * Producto.cantidad_stock).label('valor')
    ).join(Producto).filter(Producto.activo == True).group_by(Categoria.id, Categoria.nombre).all()

    movimientos_30dias = db.session.query(
        func.date(Venta.fecha).label('fecha'),
        func.sum(Venta.total).label('cantidad')
    ).join(Producto, Producto.id == Venta.producto_id).filter(
        Producto.se_vende == True
    ).group_by(func.date(Venta.fecha)).order_by(func.date(Venta.fecha)).all()

    resumen_mensual = _resumen_mensual_6_meses()

    return render_template(
        'main/reportes.html',
        productos_vendidos=productos_vendidos,
        valor_por_categoria=valor_por_categoria,
        movimientos_30dias=movimientos_30dias,
        resumen_mensual=resumen_mensual,
        meses_labels=[m['mes'] for m in resumen_mensual],
        ventas_mensuales_data=[round(m['ventas'], 2) for m in resumen_mensual],
        utilidad_mensual_data=[round(m['utilidad'], 2) for m in resumen_mensual],
        gastos_stock_data=[round(m['gasto_stock'], 2) for m in resumen_mensual]
    )
