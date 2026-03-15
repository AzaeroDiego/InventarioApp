import os
from app import create_app, db
from app.models import Usuario, Categoria, Producto, MovimientoStock

app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    """Contexto para flask shell"""
    return {
        'db': db,
        'Usuario': Usuario,
        'Categoria': Categoria,
        'Producto': Producto,
        'MovimientoStock': MovimientoStock
    }


@app.cli.command()
def init_db():
    """Inicializar base de datos con datos de prueba"""
    db.create_all()
    
    # Crear categorías
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
    categoria_alcohol = Categoria.query.filter_by(nombre='Bebidas Alcohólicas').first()
    categoria_noalcohol = Categoria.query.filter_by(nombre='Bebidas No Alcohólicas').first()
    
    productos_data = [
        {
            'nombre': 'Rebelde Paquete',
            'sku': 'REB-PKG',
            'categoria_id': categoria_alcohol.id,
            'descripcion': 'Cerveza Rebelde en formato paquete',
            'precio': 45.00,
            'cantidad_stock': 150,
            'stock_minimo': 20
        },
        {
            'nombre': 'Party Box Lata',
            'sku': 'PTY-LT',
            'categoria_id': categoria_noalcohol.id,
            'descripcion': 'Bebida energética Party Box en lata',
            'precio': 25.00,
            'cantidad_stock': 200,
            'stock_minimo': 30
        },
        {
            'nombre': 'Party Box 3L',
            'sku': 'PTY-3L',
            'categoria_id': categoria_noalcohol.id,
            'descripcion': 'Bebida energética Party Box en botellon 3L',
            'precio': 60.00,
            'cantidad_stock': 80,
            'stock_minimo': 15
        },
        {
            'nombre': 'Pisco',
            'sku': 'PSC-750',
            'categoria_id': categoria_alcohol.id,
            'descripcion': 'Pisco peruano 750ml',
            'precio': 120.00,
            'cantidad_stock': 50,
            'stock_minimo': 10
        },
    ]
    
    for prod_data in productos_data:
        if not Producto.query.filter_by(sku=prod_data['sku']).first():
            producto = Producto(**prod_data)
            db.session.add(producto)
    
    db.session.commit()
    
    # Generar códigos QR
    from app.utils import generate_qr
    productos = Producto.query.all()
    for producto in productos:
        if not producto.codigo_qr:
            generate_qr(producto)
    
    print('Base de datos inicializada correctamente')


@app.cli.command()
def create_user():
    """Crear usuario de prueba"""
    email = input('Email: ').strip().lower()
    nombre = input('Nombre completo: ').strip()
    password = input('Contraseña: ')
    
    if Usuario.query.filter_by(email=email).first():
        print('El usuario ya existe')
        return
    
    usuario = Usuario(nombre_completo=nombre, email=email)
    usuario.set_password(password)
    
    db.session.add(usuario)
    db.session.commit()
    
    print(f'Usuario {email} creado exitosamente')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
