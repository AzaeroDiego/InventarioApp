#!/usr/bin/env python
"""Script para corregir precios en la base de datos"""
import os
from app import create_app, db
from app.models import Producto

app = create_app(os.environ.get('FLASK_ENV', 'development'))

with app.app_context():
    print("Corrigiendo precios...")
    
    # Precios correctos en soles
    precios_correctos = {
        'REB-PKG': 45.00,
        'PTY-LT': 25.00,
        'PTY-3L': 60.00,
        'PSC-750': 120.00,
        'PTY-YRD-3L': 69.90,
        'YRD-ESP-MUJ': 59.90,
        'JRB-GMA': 0.00
    }
    
    for sku, precio_correcto in precios_correctos.items():
        producto = Producto.query.filter_by(sku=sku).first()
        if producto:
            print(f"  {sku}: {producto.precio} → {precio_correcto}")
            producto.precio = precio_correcto
    
    db.session.commit()
    print("✅ Precios corregidos correctamente!")
