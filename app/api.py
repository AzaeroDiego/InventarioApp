from flask import Blueprint, jsonify, request
from flask_login import login_required
from app import db
from app.models import Producto, AlertaStock, MovimientoStock
from datetime import datetime
import csv
from io import StringIO

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/alertas/no-leidas', methods=['GET'])
@login_required
def get_alertas_no_leidas():
    """Obtener alertas no leídas como JSON"""
    alertas = AlertaStock.query.filter_by(leida=False).all()
    return jsonify({
        'count': len(alertas),
        'alertas': [{
            'id': a.id,
            'producto_nombre': a.producto.nombre,
            'mensaje': a.mensaje,
            'fecha': a.fecha_creacion.isoformat()
        } for a in alertas]
    })


@api_bp.route('/producto/<int:id>/qr', methods=['GET'])
@login_required
def get_codigo_qr(id):
    """Obtener URL del código QR de un producto"""
    producto = Producto.query.get_or_404(id)
    return jsonify({
        'id': producto.id,
        'nombre': producto.nombre,
        'sku': producto.sku,
        'qr_url': producto.codigo_qr
    })


@api_bp.route('/reportes/exportar-csv', methods=['GET'])
@login_required
def exportar_csv():
    """Exportar reporte a CSV"""
    tipo = request.args.get('tipo', 'productos', type=str)
    
    if tipo == 'productos':
        productos = Producto.query.filter_by(activo=True).all()
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['SKU', 'Nombre', 'Categoría', 'Precio', 'Stock', 'Stock Mínimo', 'Valor Total'])
        
        for p in productos:
            writer.writerow([
                p.sku,
                p.nombre,
                p.categoria.nombre,
                f"{p.precio:.2f}",
                p.cantidad_stock,
                p.stock_minimo,
                f"{p.valor_total:.2f}"
            ])
        
        response_output = output.getvalue()
        output.close()
        
        return response_output, 200, {
            'Content-Disposition': f'attachment; filename=productos_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv',
            'Content-Type': 'text/csv'
        }
    
    elif tipo == 'movimientos':
        inicio = request.args.get('inicio', type=str)
        fin = request.args.get('fin', type=str)
        
        query = MovimientoStock.query
        
        if inicio:
            query = query.filter(MovimientoStock.fecha >= datetime.fromisoformat(inicio))
        if fin:
            query = query.filter(MovimientoStock.fecha <= datetime.fromisoformat(fin))
        
        movimientos = query.all()
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Fecha', 'Tipo', 'Producto', 'Cantidad', 'Motivo', 'Usuario'])
        
        for m in movimientos:
            writer.writerow([
                m.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                m.tipo,
                m.producto.nombre,
                m.cantidad,
                m.motivo or '-',
                m.usuario.nombre_completo
            ])
        
        response_output = output.getvalue()
        output.close()
        
        return response_output, 200, {
            'Content-Disposition': f'attachment; filename=movimientos_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv',
            'Content-Type': 'text/csv'
        }
    
    return jsonify({'error': 'Tipo de reporte no válido'}), 400


@api_bp.route('/estadisticas', methods=['GET'])
@login_required
def get_estadisticas():
    """Obtener estadísticas de la aplicación"""
    from sqlalchemy import func
    
    # Contar productos
    total_productos = Producto.query.filter_by(activo=True).count()
    bajo_stock = Producto.query.filter(
        (Producto.activo == True) & (Producto.cantidad_stock < Producto.stock_minimo)
    ).count()
    sin_stock = Producto.query.filter(
        (Producto.activo == True) & (Producto.cantidad_stock == 0)
    ).count()
    
    # Valor total
    valor_total = db.session.query(
        func.sum(Producto.precio * Producto.cantidad_stock)
    ).filter(Producto.activo == True).scalar() or 0
    
    # Últimos movimientos
    desde_hace = request.args.get('dias', 7, type=int)
    from datetime import timedelta
    hace_x_dias = datetime.utcnow() - timedelta(days=desde_hace)
    
    entradas = db.session.query(func.count(MovimientoStock.id)).filter(
        (MovimientoStock.tipo == 'entrada') & (MovimientoStock.fecha >= hace_x_dias)
    ).scalar() or 0
    
    salidas = db.session.query(func.count(MovimientoStock.id)).filter(
        (MovimientoStock.tipo == 'salida') & (MovimientoStock.fecha >= hace_x_dias)
    ).scalar() or 0
    
    return jsonify({
        'total_productos': total_productos,
        'bajo_stock': bajo_stock,
        'sin_stock': sin_stock,
        'valor_total': float(valor_total),
        'entradas_recientes': entradas,
        'salidas_recientes': salidas
    })
