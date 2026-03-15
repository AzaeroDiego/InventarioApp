#!/usr/bin/env python
"""Script para inicializar la base de datos"""
import os
from app import create_app, db
from app.models import Usuario, Categoria, Producto, Venta

# Crear app
app = create_app(os.environ.get('FLASK_ENV', 'development'))

with app.app_context():
    print("Creando tablas...")
    db.create_all()
    
    # Crear categorías
    print("Creando categorías...")
    categorias_data = [
        {'nombre': 'Bebidas Alcohólicas', 'color': '#e74c3c'},
        {'nombre': 'Bebidas No Alcohólicas', 'color': '#3498db'},
        {'nombre': 'Snacks', 'color': '#f39c12'},
        {'nombre': 'Otros', 'color': '#95a5a6'},
    ]
    
    for cat_data in categorias_data:
        if not Categoria.query.filter_by(nombre=cat_data['nombre']).first():
            categoria = Categoria(**cat_data)
            db.session.add(categoria)
    
    db.session.commit()
    
    # Crear productos
    print("Creando productos...")
    categoria_alcohol = Categoria.query.filter_by(nombre='Bebidas Alcohólicas').first()
    categoria_noalcohol = Categoria.query.filter_by(nombre='Bebidas No Alcohólicas').first()
    
    productos_data = [
        {
            'nombre': 'Rebelde Paquete',
            'sku': 'REB-PKG',
            'categoria_id': categoria_alcohol.id,
            'descripcion': 'Cerveza Rebelde en formato paquete',
            'precio': 3.5,
            'cantidad_stock': 150,
            'stock_minimo': 20,
            'litros_por_unidad': 2.5
        },
        {
            'nombre': 'Party Box Lata',
            'sku': 'PTY-LT',
            'categoria_id': categoria_noalcohol.id,
            'descripcion': 'Bebida energética Party Box en lata (2.5L)',
            'precio': 3.0,
            'cantidad_stock': 200,
            'stock_minimo': 30,
            'litros_por_unidad': 2.5
        },
        {
            'nombre': 'Party Box 3L',
            'sku': 'PTY-3L',
            'categoria_id': categoria_noalcohol.id,
            'descripcion': 'Bebida energética Party Box en botellon 3L',
            'precio': 31.51,
            'cantidad_stock': 80,
            'stock_minimo': 15,
            'litros_por_unidad': 3.0
        },
        {
            'nombre': 'Pisco',
            'sku': 'PSC-750',
            'categoria_id': categoria_alcohol.id,
            'descripcion': 'Pisco peruano 750ml',
            'precio': 0.75,
            'cantidad_stock': 50,
            'stock_minimo': 10,
            'litros_por_unidad': 0.75
        },
        {
            'nombre': 'Party Box Yarda 3L',
            'sku': 'PTY-YRD-3L',
            'categoria_id': categoria_noalcohol.id,
            'descripcion': 'Mezcla premium Party Box en botellón Yarda 3L',
            'precio': 69.90,
            'cantidad_stock': 0,
            'stock_minimo': 1,
            'activo': True,
            'litros_por_unidad': 3.0
        },
        {
            'nombre': 'Yarda 3L Especial Día Mujer',
            'sku': 'YRD-ESP-MUJ',
            'categoria_id': categoria_noalcohol.id,
            'descripcion': 'Edición especial Día Mujer - Yarda 3L',
            'precio': 59.90,
            'cantidad_stock': 0,
            'stock_minimo': 1,
            'activo': False,
            'litros_por_unidad': 3.0
        },
        {
            'nombre': 'Jarabe de Goma',
            'sku': 'JRB-GMA',
            'categoria_id': categoria_noalcohol.id,
            'descripcion': 'Jarabe de Goma para mezclas',
            'precio': 0.0,
            'cantidad_stock': 100,
            'stock_minimo': 10,
            'activo': True,
            'litros_por_unidad': 0.0
        },
    ]
    
    for prod_data in productos_data:
        if not Producto.query.filter_by(sku=prod_data['sku']).first():
            producto = Producto(**prod_data)
            db.session.add(producto)
    
    db.session.commit()
    
    # Crear usuario de prueba
    print("Creando usuario de prueba...")
    if not Usuario.query.filter_by(email='demo@example.com').first():
        usuario = Usuario()
        usuario.email = 'demo@example.com'
        usuario.nombre_completo = 'Usuario Demo'
        usuario.set_password('123456')
        db.session.add(usuario)
    
    db.session.commit()
    
    print("✅ Base de datos inicializada correctamente!")
    print(f"✅ Usuario: demo@example.com / Contraseña: 123456")
    print(f"✅ Categorías creadas: 4")
    print(f"✅ Productos creados: 7")
