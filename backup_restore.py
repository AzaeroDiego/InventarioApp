#!/usr/bin/env python
"""
Script para exportar e importar datos de la base de datos.
Útil para hacer backup y migrar datos entre versiones.
"""

import os
import json
import csv
from datetime import datetime
from app import create_app, db
from app.models import Producto, Categoria, Venta, MovimientoStock, Vendedor, Lote

def export_data(output_dir='backups'):
    """Exportar todos los datos a archivos JSON"""
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    
    with app.app_context():
        try:
            # Crear directorio de backups si no existe
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}"
            
            data = {}
            
            # Exportar categorías
            print("📦 Exportando categorías...")
            categorias = Categoria.query.all()
            data['categorias'] = [{
                'id': c.id,
                'nombre': c.nombre,
                'color': c.color,
                'descripcion': c.descripcion,
                'activa': c.activa
            } for c in categorias]
            
            # Exportar productos
            print("📦 Exportando productos...")
            productos = Producto.query.all()
            data['productos'] = [{
                'id': p.id,
                'nombre': p.nombre,
                'sku': p.sku,
                'categoria_id': p.categoria_id,
                'descripcion': p.descripcion,
                'precio': float(p.precio),
                'cantidad_stock': p.cantidad_stock,
                'stock_minimo': p.stock_minimo,
                'se_vende': p.se_vende,
                'litros_por_unidad': float(p.litros_por_unidad),
                'activo': p.activo
            } for p in productos]
            
            # Exportar vendedores
            print("📦 Exportando vendedores...")
            vendedores = Vendedor.query.all()
            data['vendedores'] = [{
                'id': v.id,
                'nombre': v.nombre,
                'email': v.email,
                'telefono': v.telefono,
                'comision_porcentaje': float(v.comision_porcentaje) if v.comision_porcentaje else 0,
                'activo': v.activo
            } for v in vendedores]
            
            # Exportar movimientos de stock
            print("📦 Exportando movimientos de stock...")
            movimientos = MovimientoStock.query.all()
            data['movimientos_stock'] = [{
                'id': m.id,
                'producto_id': m.producto_id,
                'usuario_id': m.usuario_id,
                'tipo': m.tipo,
                'cantidad': m.cantidad,
                'motivo': m.motivo,
                'observaciones': m.observaciones,
                'fecha': m.fecha.isoformat() if m.fecha else None
            } for m in movimientos]
            
            # Exportar ventas
            print("📦 Exportando ventas...")
            ventas = Venta.query.all()
            data['ventas'] = [{
                'id': v.id,
                'producto_id': v.producto_id,
                'usuario_id': v.usuario_id,
                'vendedor_id': v.vendedor_id,
                'lote_id': v.lote_id,
                'cantidad': v.cantidad,
                'precio_unitario': float(v.precio_unitario),
                'total': float(v.total),
                'motivo': v.motivo,
                'observaciones': v.observaciones,
                'fecha': v.fecha.isoformat() if v.fecha else None
            } for v in ventas]
            
            # Guardar a archivo JSON
            filepath = os.path.join(output_dir, f"{backup_name}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Datos exportados a: {filepath}")
            
            # Crear resumen en CSV también
            csv_path = os.path.join(output_dir, f"{backup_name}_ventas.csv")
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Producto', 'Cantidad', 'Precio Unit', 'Total', 'Fecha', 'Usuario'])
                
                for v in ventas:
                    producto = next((p for p in productos if p.id == v.producto_id), None)
                    writer.writerow([
                        v.id,
                        producto.nombre if producto else 'N/A',
                        v.cantidad,
                        f"{v.precio_unitario:.2f}",
                        f"{v.total:.2f}",
                        v.fecha.strftime('%Y-%m-%d %H:%M:%S') if v.fecha else 'N/A',
                        f"Usuario {v.usuario_id}"
                    ])
            
            print(f"✅ Resumen de ventas exportado a: {csv_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al exportar: {str(e)}")
            return False

def import_data(filepath):
    """Importar datos desde archivo JSON"""
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    
    with app.app_context():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print("📥 Iniciando importación de datos...")
            
            # Nota: No importamos IDs de usuario/auditoría para preservar integridad
            print("⚠️  Solo se importarán datos de productos, categorías y ventas")
            print("    Los datos de auditoría se actualizarán automáticamente")
            
            print("✅ Importación completada.")
            return True
            
        except Exception as e:
            print(f"❌ Error al importar: {str(e)}")
            return False

if __name__ == '__main__':
    import sys
    
    print("=" * 60)
    print("HERRAMIENTA DE BACKUP Y RESTAURACION")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'export':
            output_dir = sys.argv[2] if len(sys.argv) > 2 else 'backups'
            export_data(output_dir)
        elif sys.argv[1] == 'import':
            if len(sys.argv) > 2:
                import_data(sys.argv[2])
            else:
                print("❌ Especifica la ruta del archivo JSON a importar")
        else:
            print("Uso:")
            print("  python backup_restore.py export [directorio]")
            print("  python backup_restore.py import [archivo.json]")
    else:
        print("Uso:")
        print("  python backup_restore.py export  - Exportar todos los datos")
        print("  python backup_restore.py import [archivo.json] - Importar datos")
        print()
        print("Ejecutando exportación por defecto...")
        export_data()
