from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app import db
from app.models import Producto, Categoria, MovimientoStock, AlertaStock, Venta, Vendedor, Lote, IngredienteLote, Usuario
from app.utils import generate_qr, allowed_file
import os

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Página de inicio"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard con resumen de inventario"""
    # Contar productos
    total_productos = Producto.query.filter_by(activo=True).count()
    
    # Productos con bajo stock
    productos_bajo_stock = Producto.query.filter(
        (Producto.activo == True) & (Producto.cantidad_stock < Producto.stock_minimo)
    ).all()
    
    # Valor total del inventario
    valor_total = db.session.query(
        func.sum(Producto.precio * Producto.cantidad_stock)
    ).filter(Producto.activo == True).scalar() or 0
    
    # Últimos movimientos
    movimientos_recientes = MovimientoStock.query.order_by(
        desc(MovimientoStock.fecha)
    ).limit(10).all()
    
    # Alertas no leídas
    alertas_no_leidas = AlertaStock.query.filter_by(leida=False).count()
    
    # Estadísticas de movimientos (últimos 7 días)
    hace_7_dias = datetime.utcnow() - timedelta(days=7)
    
    entradas_7dias = db.session.query(func.count(MovimientoStock.id)).filter(
        (MovimientoStock.tipo == 'entrada') & (MovimientoStock.fecha >= hace_7_dias)
    ).scalar() or 0
    
    salidas_7dias = db.session.query(func.count(MovimientoStock.id)).filter(
        (MovimientoStock.tipo == 'salida') & (MovimientoStock.fecha >= hace_7_dias)
    ).scalar() or 0
    
    # Ventas del día
    hoy = datetime.utcnow().date()
    ventas_hoy = Venta.query.filter(
        func.date(Venta.fecha) == hoy
    ).all()
    
    total_ventas_hoy = db.session.query(func.sum(Venta.total)).filter(
        func.date(Venta.fecha) == hoy
    ).scalar() or 0
    
    return render_template('main/dashboard.html',
                         total_productos=total_productos,
                         productos_bajo_stock=productos_bajo_stock,
                         valor_total=valor_total,
                         movimientos_recientes=movimientos_recientes,
                         alertas_no_leidas=alertas_no_leidas,
                         entradas_recientes=entradas_7dias,
                         salidas_recientes=salidas_7dias,
                         ventas_hoy=ventas_hoy,
                         total_ventas_hoy=total_ventas_hoy)


@main_bp.route('/productos')
@login_required
def productos():
    """Lista de productos"""
    pagina = request.args.get('pagina', 1, type=int)
    buscar = request.args.get('buscar', '', type=str)
    categoria_id = request.args.get('categoria', 0, type=int)
    estado = request.args.get('estado', 'todos', type=str)
    
    query = Producto.query.filter_by(activo=True)
    
    if buscar:
        query = query.filter(
            (Producto.nombre.ilike(f'%{buscar}%')) |
            (Producto.sku.ilike(f'%{buscar}%'))
        )
    
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)
    
    if estado == 'bajo_stock':
        query = query.filter(Producto.cantidad_stock < Producto.stock_minimo)
    elif estado == 'sin_stock':
        query = query.filter_by(cantidad_stock=0)
    
    categorias = Categoria.query.filter_by(activa=True).all()
    
    productos = query.paginate(page=pagina, per_page=20)
    
    return render_template('main/productos.html',
                         productos=productos,
                         categorias=categorias,
                         buscar=buscar,
                         categoria_id=categoria_id,
                         estado=estado)


@main_bp.route('/producto/nuevo', methods=['GET', 'POST'])
@login_required
def crear_producto():
    """Crear nuevo producto"""
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        sku = request.form.get('sku', '').strip().upper()
        categoria_id = request.form.get('categoria_id', type=int)
        precio = request.form.get('precio', type=float)
        cantidad = request.form.get('cantidad_stock', 0, type=int)
        stock_minimo = request.form.get('stock_minimo', 5, type=int)
        se_vende = request.form.get('se_vende', '1') == '1'
        
        # Validaciones
        if not nombre or not sku or not categoria_id or not precio:
            flash('Todos los campos son requeridos.', 'error')
            return redirect(url_for('main.crear_producto'))
        
        if Producto.query.filter_by(sku=sku).first():
            flash('El SKU ya existe.', 'error')
            return redirect(url_for('main.crear_producto'))
        
        # Crear producto
        producto = Producto(
            nombre=nombre,
            sku=sku,
            categoria_id=categoria_id,
            precio=precio,
            cantidad_stock=cantidad,
            stock_minimo=stock_minimo,
            se_vende=se_vende
        )
        
        # Procesar imagen si existe
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and allowed_file(file.filename):
                import uuid
                filename = f"{uuid.uuid4().hex}_{file.filename}"
                file.save(os.path.join('static/uploads', filename))
                producto.imagen_url = f'/static/uploads/{filename}'
        
        db.session.add(producto)
        db.session.commit()
        
        # Generar código QR
        generate_qr(producto)
        
        flash('Producto creado exitosamente.', 'success')
        return redirect(url_for('main.productos'))
    
    categorias = Categoria.query.filter_by(activa=True).all()
    return render_template('main/crear_producto.html', categorias=categorias)


@main_bp.route('/producto/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    """Editar producto"""
    producto = Producto.query.get_or_404(id)
    
    if request.method == 'POST':
        producto.nombre = request.form.get('nombre', '').strip()
        producto.categoria_id = request.form.get('categoria_id', type=int)
        producto.precio = request.form.get('precio', type=float)
        producto.cantidad_stock = request.form.get('cantidad_stock', 0, type=int)
        producto.stock_minimo = request.form.get('stock_minimo', 5, type=int)
        producto.se_vende = request.form.get('se_vende', '1') == '1'
        
        # Procesar imagen si existe
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and allowed_file(file.filename):
                import uuid
                filename = f"{uuid.uuid4().hex}_{file.filename}"
                file.save(os.path.join('static/uploads', filename))
                producto.imagen_url = f'/static/uploads/{filename}'
        
        db.session.commit()
        
        flash('Producto actualizado exitosamente.', 'success')
        return redirect(url_for('main.productos'))
    
    categorias = Categoria.query.filter_by(activa=True).all()
    return render_template('main/editar_producto.html', producto=producto, categorias=categorias)


@main_bp.route('/producto/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_producto(id):
    """Eliminar (desactivar) producto"""
    producto = Producto.query.get_or_404(id)
    producto.activo = False
    db.session.commit()
    
    flash('Producto eliminado exitosamente.', 'success')
    return redirect(url_for('main.productos'))


@main_bp.route('/categorias')
@login_required
def categorias():
    """Lista de categorías"""
    categorias = Categoria.query.filter_by(activa=True).all()
    return render_template('main/categorias.html', categorias=categorias)


@main_bp.route('/categoria/nueva', methods=['GET', 'POST'])
@login_required
def crear_categoria():
    """Crear nueva categoría"""
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        color = request.form.get('color', '#3498db')
        
        if not nombre:
            flash('El nombre es requerido.', 'error')
            return redirect(url_for('main.crear_categoria'))
        
        if Categoria.query.filter_by(nombre=nombre).first():
            flash('La categoría ya existe.', 'error')
            return redirect(url_for('main.crear_categoria'))
        
        categoria = Categoria(nombre=nombre, color=color)
        db.session.add(categoria)
        db.session.commit()
        
        flash('Categoría creada exitosamente.', 'success')
        return redirect(url_for('main.categorias'))
    
    return render_template('main/crear_categoria.html')


@main_bp.route('/categoria/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_categoria(id):
    """Editar categoría"""
    categoria = Categoria.query.get_or_404(id)
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        color = request.form.get('color', '#3498db')
        
        if Categoria.query.filter(Categoria.nombre == nombre, Categoria.id != id).first():
            flash('El nombre ya está en uso.', 'error')
            return redirect(url_for('main.editar_categoria', id=id))
        
        categoria.nombre = nombre
        categoria.color = color
        db.session.commit()
        
        flash('Categoría actualizada exitosamente.', 'success')
        return redirect(url_for('main.categorias'))
    
    return render_template('main/editar_categoria.html', categoria=categoria)


@main_bp.route('/stock/movimientos')
@login_required
def movimientos_stock():
    """Historial de movimientos de stock"""
    pagina = request.args.get('pagina', 1, type=int)
    tipo = request.args.get('tipo', 'todos', type=str)
    producto_id = request.args.get('producto', 0, type=int)
    
    query = MovimientoStock.query
    
    if tipo != 'todos':
        query = query.filter_by(tipo=tipo)
    
    if producto_id:
        query = query.filter_by(producto_id=producto_id)
    
    movimientos = query.order_by(desc(MovimientoStock.fecha)).paginate(page=pagina, per_page=20)
    productos = Producto.query.filter_by(activo=True).all()
    
    return render_template('main/movimientos_stock.html',
                         movimientos=movimientos,
                         productos=productos,
                         tipo=tipo,
                         producto_id=producto_id)


@main_bp.route('/stock/entrada', methods=['GET', 'POST'])
@login_required
def entrada_stock():
    """Registrar entrada de stock"""
    if request.method == 'POST':
        producto_id = request.form.get('producto_id', type=int)
        cantidad = request.form.get('cantidad', 0, type=int)
        motivo = request.form.get('motivo', '').strip()
        
        producto = Producto.query.get_or_404(producto_id)
        
        if cantidad <= 0:
            flash('La cantidad debe ser mayor a 0.', 'error')
            return redirect(url_for('main.entrada_stock'))
        
        # Crear movimiento
        movimiento = MovimientoStock(
            producto_id=producto_id,
            usuario_id=current_user.id,
            tipo='entrada',
            cantidad=cantidad,
            motivo=motivo
        )
        
        # Actualizar stock
        producto.cantidad_stock += cantidad
        
        db.session.add(movimiento)
        db.session.commit()
        
        flash('Entrada registrada exitosamente.', 'success')
        return redirect(url_for('main.movimientos_stock'))
    
    productos = Producto.query.filter_by(activo=True).all()
    return render_template('main/entrada_stock.html', productos=productos)


@main_bp.route('/stock/salida', methods=['GET', 'POST'])
@login_required
def salida_stock():
    """Registrar salida de stock"""
    if request.method == 'POST':
        producto_id = request.form.get('producto_id', type=int)
        cantidad = request.form.get('cantidad', 0, type=int)
        motivo = request.form.get('motivo', '').strip()
        
        producto = Producto.query.get_or_404(producto_id)
        
        if cantidad <= 0:
            flash('La cantidad debe ser mayor a 0.', 'error')
            return redirect(url_for('main.salida_stock'))
        
        if cantidad > producto.cantidad_stock:
            flash('Stock insuficiente.', 'error')
            return redirect(url_for('main.salida_stock'))
        
        # Crear movimiento
        movimiento = MovimientoStock(
            producto_id=producto_id,
            usuario_id=current_user.id,
            tipo='salida',
            cantidad=cantidad,
            motivo=motivo
        )
        
        # Actualizar stock
        producto.cantidad_stock -= cantidad
        
        db.session.add(movimiento)
        db.session.commit()
        
        # Crear alerta si el stock cae por debajo del mínimo
        if producto.cantidad_stock < producto.stock_minimo:
            alerta = AlertaStock(
                producto_id=producto_id,
                tipo='bajo_stock',
                mensaje=f'{producto.nombre} tiene bajo stock ({producto.cantidad_stock} unidades)'
            )
            db.session.add(alerta)
            db.session.commit()
        
        flash('Salida registrada exitosamente.', 'success')
        return redirect(url_for('main.movimientos_stock'))
    
    productos = Producto.query.filter_by(activo=True).all()
    return render_template('main/salida_stock.html', productos=productos)


@main_bp.route('/reportes')
@login_required
def reportes():
    """Vista de reportes"""
    # Productos más vendidos (por salidas)
    productos_vendidos = db.session.query(
        Producto.nombre,
        func.sum(MovimientoStock.cantidad).label('total')
    ).join(MovimientoStock).filter(
        MovimientoStock.tipo == 'salida'
    ).group_by(Producto.id).order_by(desc('total')).limit(10).all()
    
    # Valor del inventario por categoría
    valor_por_categoria = db.session.query(
        Categoria.nombre,
        func.sum(Producto.precio * Producto.cantidad_stock).label('valor')
    ).join(Producto).filter(Producto.activo == True).group_by(Categoria.id).all()
    
    # Movimientos en los últimos 30 días
    hace_30_dias = datetime.utcnow() - timedelta(days=30)
    movimientos_30dias = db.session.query(
        func.date(MovimientoStock.fecha).label('fecha'),
        func.count(MovimientoStock.id).label('cantidad')
    ).filter(MovimientoStock.fecha >= hace_30_dias).group_by(
        func.date(MovimientoStock.fecha)
    ).all()
    
    return render_template('main/reportes.html',
                         productos_vendidos=productos_vendidos,
                         valor_por_categoria=valor_por_categoria,
                         movimientos_30dias=movimientos_30dias)


@main_bp.route('/alertas')
@login_required
def alertas():
    """Lista de alertas"""
    alertas = AlertaStock.query.filter_by(leida=False).all()
    return render_template('main/alertas.html', alertas=alertas)


@main_bp.route('/alerta/<int:id>/marcar-leida', methods=['POST'])
@login_required
def marcar_alerta_leida(id):
    """Marcar alerta como leída"""
    alerta = AlertaStock.query.get_or_404(id)
    alerta.leida = True
    db.session.commit()
    return jsonify({'estado': 'ok'})


# ===== RUTAS DE VENTAS =====

@main_bp.route('/ventas')
@login_required
def ventas():
    """Vista de ventas diarias"""
    hoy = datetime.utcnow().date()
    
    # Ventas de hoy
    ventas_hoy = Venta.query.filter(
        func.date(Venta.fecha) == hoy
    ).order_by(desc(Venta.fecha)).all()
    
    # Totales del día
    total_ventas_hoy = db.session.query(func.sum(Venta.total)).filter(
        func.date(Venta.fecha) == hoy
    ).scalar() or 0
    
    cantidad_ventas_hoy = len(ventas_hoy)
    
    return render_template('main/ventas.html',
                          ventas_hoy=ventas_hoy,
                          total_ventas_hoy=total_ventas_hoy,
                          cantidad_ventas_hoy=cantidad_ventas_hoy)


@main_bp.route('/venta/nueva', methods=['GET', 'POST'])
@login_required
def nueva_venta():
    """Registrar nueva venta"""
    # Filtrar solo productos que se venden
    productos = Producto.query.filter_by(activo=True, se_vende=True).all()
    vendedores = Vendedor.query.filter_by(activo=True).all()
    
    if request.method == 'POST':
        try:
            producto_id = request.form.get('producto_id', type=int)
            cantidad = request.form.get('cantidad', type=int)
            precio_unitario = request.form.get('precio_unitario', type=float)
            motivo = request.form.get('motivo', 'Venta normal')
            observaciones = request.form.get('observaciones', '')
            vendedor_id = request.form.get('vendedor_id', type=int) if request.form.get('vendedor_id') else None
            
            if not producto_id or not cantidad or not precio_unitario:
                flash('Todos los campos son requeridos', 'error')
                return redirect(url_for('main.nueva_venta'))
            
            producto = Producto.query.get_or_404(producto_id)
            
            # Verificar que hay stock suficiente
            if producto.cantidad_stock < cantidad:
                flash(f'Stock insuficiente. Disponible: {producto.cantidad_stock}', 'error')
                return redirect(url_for('main.nueva_venta'))
            
            if cantidad <= 0:
                flash('La cantidad debe ser mayor a cero', 'error')
                return redirect(url_for('main.nueva_venta'))
            
            # Crear venta
            total = cantidad * precio_unitario
            venta = Venta(
                producto_id=producto_id,
                usuario_id=current_user.id,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                total=total,
                motivo=motivo,
                observaciones=observaciones,
                vendedor_id=vendedor_id
            )
            
            # Disminuir stock del producto
            producto.cantidad_stock -= cantidad
            
            # Registrar movimiento de stock
            movimiento = MovimientoStock(
                producto_id=producto_id,
                usuario_id=current_user.id,
                tipo='salida',
                cantidad=cantidad,
                motivo='Venta',
                observaciones=f'Venta: {motivo}'
            )
            
            # Verificar si entra en alerta
            if producto.cantidad_stock < producto.stock_minimo:
                alerta = AlertaStock(
                    producto_id=producto_id,
                    tipo='bajo_stock',
                    mensaje=f'{producto.nombre} por debajo del stock mínimo'
                )
                db.session.add(alerta)
            
            db.session.add(venta)
            db.session.add(movimiento)
            db.session.commit()
            
            flash(f'✅ Venta registrada: {cantidad} x {producto.nombre}', 'success')
            return redirect(url_for('main.ventas'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar venta: {str(e)}', 'error')
            return redirect(url_for('main.nueva_venta'))
    
    return render_template('main/nueva_venta.html', productos=productos, vendedores=vendedores)


@main_bp.route('/historial-ventas')
@login_required
def historial_ventas():
    """Historial completo de ventas"""
    page = request.args.get('page', 1, type=int)
    
    # Filtros opcionales
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    producto_id = request.args.get('producto_id', type=int)
    
    query = Venta.query
    
    if fecha_desde:
        fecha_desde = datetime.fromisoformat(fecha_desde)
        query = query.filter(Venta.fecha >= fecha_desde)
    
    if fecha_hasta:
        fecha_hasta = datetime.fromisoformat(fecha_hasta)
        query = query.filter(Venta.fecha <= fecha_hasta)
    
    if producto_id:
        query = query.filter(Venta.producto_id == producto_id)
    
    ventas = query.order_by(desc(Venta.fecha)).paginate(page=page, per_page=20)
    
    # Total de ventas en el filtro
    total_vendido = db.session.query(func.sum(Venta.total)).filter(
        Venta.query.statement.whereclause
    ).scalar() or 0
    
    productos = Producto.query.filter_by(activo=True).all()
    
    return render_template('main/historial_ventas.html',
                          ventas=ventas,
                          total_vendido=total_vendido,
                          productos=productos)


# ===== RUTAS DE VENDEDORES =====

@main_bp.route('/vendedores')
@login_required
def vendedores():
    """Lista de vendedores"""
    vendedores = Vendedor.query.all()
    return render_template('main/vendedores.html', vendedores=vendedores)


@main_bp.route('/vendedor/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_vendedor():
    """Crear nuevo vendedor"""
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre')
            email = request.form.get('email', '').strip() or None
            telefono = request.form.get('telefono', '').strip() or None
            comision = request.form.get('comision', 0, type=float)
            
            if not nombre:
                flash('El nombre es requerido', 'error')
                return redirect(url_for('main.nuevo_vendedor'))
            
            if Vendedor.query.filter_by(nombre=nombre).first():
                flash('Ya existe un vendedor con ese nombre', 'error')
                return redirect(url_for('main.nuevo_vendedor'))
            
            vendedor = Vendedor(
                nombre=nombre,
                email=email,
                telefono=telefono,
                comision_porcentaje=comision
            )
            db.session.add(vendedor)
            db.session.commit()
            
            flash(f'✅ Vendedor "{nombre}" creado exitosamente', 'success')
            return redirect(url_for('main.vendedores'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear vendedor: {str(e)}', 'error')
            return redirect(url_for('main.nuevo_vendedor'))
    
    return render_template('main/nuevo_vendedor.html')


@main_bp.route('/vendedor/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_vendedor(id):
    """Editar vendedor"""
    vendedor = Vendedor.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            vendedor.nombre = request.form.get('nombre')
            vendedor.email = request.form.get('email', '').strip() or None
            vendedor.telefono = request.form.get('telefono', '').strip() or None
            vendedor.comision_porcentaje = request.form.get('comision', 0, type=float)
            vendedor.activo = request.form.get('activo') == 'on'
            
            db.session.commit()
            
            flash('✅ Vendedor actualizado', 'success')
            return redirect(url_for('main.vendedores'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('main/editar_vendedor.html', vendedor=vendedor)


@main_bp.route('/vendedor/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_vendedor(id):
    """Eliminar vendedor"""
    vendedor = Vendedor.query.get_or_404(id)
    try:
        db.session.delete(vendedor)
        db.session.commit()
        flash('✅ Vendedor eliminado', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('main.vendedores'))


# ===== RUTAS DE ADMIN - EDICIÓN DE PRODUCTOS =====

@main_bp.route('/admin/productos')
@login_required
def admin_productos():
    """Panel de administración de productos (todos, activos e inactivos)"""
    productos = Producto.query.all()
    return render_template('main/admin_productos.html', productos=productos)


@main_bp.route('/admin/producto/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def admin_editar_producto(id):
    """Editar producto (admin)"""
    producto = Producto.query.get_or_404(id)
    categorias = Categoria.query.all()
    
    if request.method == 'POST':
        try:
            producto.nombre = request.form.get('nombre')
            producto.sku = request.form.get('sku')
            producto.categoria_id = request.form.get('categoria_id', type=int)
            producto.precio = request.form.get('precio', type=float)
            producto.cantidad_stock = request.form.get('cantidad_stock', type=int)
            producto.stock_minimo = request.form.get('stock_minimo', type=int)
            producto.descripcion = request.form.get('descripcion', '')
            producto.activo = request.form.get('activo') == 'on'
            
            db.session.commit()
            flash('✅ Producto actualizado', 'success')
            return redirect(url_for('main.admin_productos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('main/admin_editar_producto.html', producto=producto, categorias=categorias)


# ===== RUTAS DE PREPARACIÓN DE LOTES =====

@main_bp.route('/lotes')
@login_required
def lotes():
    """Lista de lotes preparados"""
    lotes = Lote.query.order_by(desc(Lote.fecha_preparacion)).all()
    return render_template('main/lotes.html', lotes=lotes)


@main_bp.route('/lote/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_lote():
    """Preparar nuevo lote (mezclar productos)"""
    # Filtrar solo ingredientes (productos que NO se venden)
    productos = Producto.query.filter_by(activo=True, se_vende=False).all()
    
    if request.method == 'POST':
        import json
        try:
            nombre = request.form.get('nombre')
            descripcion = request.form.get('descripcion', '')
            cantidad_preparada = request.form.get('cantidad_preparada', type=int)
            ingredientes_json = request.form.get('ingredientes_json', '[]')
            
            if not nombre or not cantidad_preparada:
                flash('Nombre y cantidad son requeridos', 'error')
                return redirect(url_for('main.nuevo_lote'))
            
            # Parsear ingredientes desde JSON
            try:
                ingredientes_arr = json.loads(ingredientes_json)
            except:
                ingredientes_arr = []
            
            if not ingredientes_arr:
                flash('Debe agregar al menos un ingrediente', 'error')
                return redirect(url_for('main.nuevo_lote'))
            
            costo_total = 0
            ingredientes_data = []
            
            # Procesar ingredientes
            for ing in ingredientes_arr:
                prod_id = ing.get('producto_id')
                cantidad = ing.get('cantidad_usada', 0)
                
                if not prod_id or cantidad <= 0:
                    continue
                
                producto = Producto.query.get(int(prod_id))
                
                if not producto:
                    flash(f'Producto no encontrado', 'error')
                    return redirect(url_for('main.nuevo_lote'))
                
                # Verificar stock
                if producto.cantidad_stock < cantidad:
                    flash(f'Stock insuficiente de {producto.nombre}: tienes {producto.cantidad_stock}, necesitas {cantidad}', 'error')
                    return redirect(url_for('main.nuevo_lote'))
                
                costo_ingrediente = cantidad * producto.precio
                costo_total += costo_ingrediente
                
                ingredientes_data.append({
                    'producto_id': int(prod_id),
                    'cantidad': cantidad,
                    'costo_unitario': producto.precio,
                    'costo_total': costo_ingrediente
                })
            
            if not ingredientes_data:
                flash('Debe agregar al menos un ingrediente válido', 'error')
                return redirect(url_for('main.nuevo_lote'))
            
            # Crear lote
            lote = Lote(
                nombre=nombre,
                descripcion=descripcion,
                cantidad_preparada=cantidad_preparada,
                costo_total=costo_total,
                usuario_id=current_user.id
            )
            
            db.session.add(lote)
            db.session.flush()  # Para obtener el ID del lote
            
            # Agregar ingredientes y descontar stock
            for ing_data in ingredientes_data:
                ingrediente = IngredienteLote(
                    lote_id=lote.id,
                    producto_id=ing_data['producto_id'],
                    cantidad_usada=ing_data['cantidad'],
                    costo_unitario=ing_data['costo_unitario']
                )
                db.session.add(ingrediente)
                
                # Descontar del stock
                producto = Producto.query.get(ing_data['producto_id'])
                producto.cantidad_stock -= ing_data['cantidad']
                
                # Crear movimiento
                movimiento = MovimientoStock(
                    producto_id=ing_data['producto_id'],
                    usuario_id=current_user.id,
                    tipo='salida',
                    cantidad=ing_data['cantidad'],
                    motivo='Preparación de lote',
                    observaciones=f'Lote: {nombre}'
                )
                db.session.add(movimiento)
            
            # Si el lote se llama "Yarda" o contiene "Yarda", aumentar stock de "Party Box Yarda 3L"
            if 'yarda' in nombre.lower():
                producto_yarda = Producto.query.filter_by(sku='PTY-YRD-3L').first()
                if producto_yarda:
                    producto_yarda.cantidad_stock += cantidad_preparada
                    
                    # Crear movimiento de entrada para el producto final
                    movimiento_yarda = MovimientoStock(
                        producto_id=producto_yarda.id,
                        usuario_id=current_user.id,
                        tipo='entrada',
                        cantidad=cantidad_preparada,
                        motivo='Preparación de lote',
                        observaciones=f'Lote Yarda preparado: {nombre}'
                    )
                    db.session.add(movimiento_yarda)
            
            db.session.commit()
            flash(f'✅ Lote "{nombre}" preparado con {cantidad_preparada} unidades', 'success')
            return redirect(url_for('main.lotes'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al preparar lote: {str(e)}', 'error')
            return redirect(url_for('main.nuevo_lote'))
    
    # Convertir productos a JSON para el frontend
    import json
    productos_json = json.dumps([{
        'id': p.id,
        'nombre': p.nombre,
        'precio': float(p.precio),
        'cantidad_stock': p.cantidad_stock,
        'activo': p.activo
    } for p in productos])
    
    return render_template('main/nuevo_lote.html', productos_json=productos_json)


# ============ ADMINISTRACIÓN DE USUARIOS ============

@main_bp.route('/admin/usuarios')
@login_required
def admin_usuarios():
    """Administración de usuarios y permisos"""
    # Solo admin o usuarios con permisos especiales
    if not current_user.has_permisos:
        flash('No tienes permisos para acceder a esta sección.', 'error')
        return redirect(url_for('main.dashboard'))
    
    usuarios = Usuario.query.order_by(Usuario.fecha_creacion.desc()).all()
    return render_template('main/admin_usuarios.html', usuarios=usuarios)


@main_bp.route('/admin/usuario/<int:id>/editar-permisos', methods=['POST'])
@login_required
def editar_permisos_usuario(id):
    """Editar permisos de un usuario"""
    if not current_user.has_permisos:
        flash('No tienes permisos para esta acción.', 'error')
        return redirect(url_for('main.dashboard'))
    
    usuario = Usuario.query.get_or_404(id)
    
    # Cambiar permisos
    has_permisos = request.form.get('has_permisos', '0') == '1'
    usuario.has_permisos = has_permisos
    
    # Cambiar rol si se proporciona
    rol = request.form.get('rol', usuario.rol)
    if rol in ['admin', 'vendedor', 'gerente']:
        usuario.rol = rol
    
    db.session.commit()
    
    status = "activados" if has_permisos else "desactivados"
    flash(f'Permisos de {usuario.nombre_completo} {status}.', 'success')
    
    return redirect(url_for('main.admin_usuarios'))


@main_bp.route('/admin/usuario/<int:id>/cambiar-estado', methods=['POST'])
@login_required
def cambiar_estado_usuario(id):
    """Activar/desactivar usuario"""
    if not current_user.has_permisos:
        flash('No tienes permisos para esta acción.', 'error')
        return redirect(url_for('main.dashboard'))
    
    usuario = Usuario.query.get_or_404(id)
    usuario.activo = not usuario.activo
    db.session.commit()
    
    status = "activado" if usuario.activo else "desactivado"
    flash(f'Usuario {usuario.nombre_completo} {status}.', 'success')
    
    return redirect(url_for('main.admin_usuarios'))


@main_bp.route('/admin/usuario/<int:id>/resetear-contraseña', methods=['POST'])
@login_required
def resetear_contrasena(id):
    """Resetear contraseña de usuario a contraseña temporal"""
    if not current_user.has_permisos:
        flash('No tienes permisos para esta acción.', 'error')
        return redirect(url_for('main.dashboard'))
    
    usuario = Usuario.query.get_or_404(id)
    
    # Contraseña temporal = 123456 (usuario debe cambiarla)
    temp_password = '123456'
    usuario.set_password(temp_password)
    db.session.commit()
    
    flash(f'Contraseña de {usuario.nombre_completo} reseteada a: {temp_password}', 'warning')
    
    return redirect(url_for('main.admin_usuarios'))


@main_bp.route('/api/usuarios/lista')
@login_required
def api_usuarios_lista():
    """API para obtener lista de usuarios activos (JSON)"""
    usuarios = Usuario.query.filter_by(activo=True).all()
    return jsonify([{
        'id': u.id,
        'nombre_completo': u.nombre_completo,
        'email': u.email,
        'rol': u.rol,
        'has_permisos': u.has_permisos
    } for u in usuarios])

