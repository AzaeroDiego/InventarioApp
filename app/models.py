from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class Usuario(UserMixin, db.Model):
    """Modelo de usuario para autenticación"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    has_permisos = db.Column(db.Boolean, default=True)  # SI=Permisos completos, NO=Solo lectura
    rol = db.Column(db.String(50), default='vendedor')  # admin, vendedor, etc.
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    movimientos = db.relationship('MovimientoStock', backref='usuario', lazy=True)
    
    def set_password(self, password):
        """Encriptar contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Usuario {self.email}>'


@login_manager.user_loader
def load_user(user_id):
    """Cargar usuario por ID"""
    return Usuario.query.get(int(user_id))


class Categoria(db.Model):
    """Modelo de categorías de productos"""
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    color = db.Column(db.String(7), default='#3498db')  # Color hex
    descripcion = db.Column(db.Text)
    activa = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    productos = db.relationship('Producto', backref='categoria', lazy=True)
    
    def __repr__(self):
        return f'<Categoria {self.nombre}>'


class Producto(db.Model):
    """Modelo de productos del inventario"""
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False, index=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    cantidad_stock = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=5)
    litros_por_unidad = db.Column(db.Float, default=1.0)  # Conversión de unidades a litros
    imagen_url = db.Column(db.String(255))
    codigo_qr = db.Column(db.String(255))  # Ruta del código QR
    se_vende = db.Column(db.Boolean, default=True)  # SI=Se vende, NO=Es ingrediente para lotes
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    movimientos = db.relationship('MovimientoStock', backref='producto', lazy=True, cascade='all, delete-orphan')
    
    @property
    def litros_total(self):
        """Calcular total de litros en stock"""
        return self.cantidad_stock * self.litros_por_unidad
    
    @property
    def bajo_stock(self):
        """Verificar si el producto tiene bajo stock"""
        return self.cantidad_stock < self.stock_minimo
    
    @property
    def valor_total(self):
        """Calcular valor total del stock"""
        return self.precio * self.cantidad_stock
    
    def __repr__(self):
        return f'<Producto {self.nombre}>'


class MovimientoStock(db.Model):
    """Modelo para registrar entradas y salidas de stock"""
    __tablename__ = 'movimientos_stock'
    
    TIPOS_MOVIMIENTO = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
        ('devolucion', 'Devolución'),
        ('correccion', 'Corrección'),
    ]
    
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # entrada, salida, ajuste, etc.
    cantidad = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(200))
    observaciones = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<MovimientoStock {self.tipo} - {self.cantidad}>'


class AlertaStock(db.Model):
    """Modelo para alertas de bajo stock"""
    __tablename__ = 'alertas_stock'
    
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    tipo = db.Column(db.String(50), default='bajo_stock')
    mensaje = db.Column(db.String(255))
    leida = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación
    producto = db.relationship('Producto', backref='alertas')
    
    def __repr__(self):
        return f'<AlertaStock {self.producto_id}>'


class Venta(db.Model):
    """Modelo para registrar ventas diarias"""
    __tablename__ = 'ventas'
    
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    vendedor_id = db.Column(db.Integer, db.ForeignKey('vendedores.id'))
    lote_id = db.Column(db.Integer, db.ForeignKey('lotes.id'))
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    motivo = db.Column(db.String(100))  # Venta normal, Descuento, Devolución, etc
    observaciones = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    producto = db.relationship('Producto', backref='ventas')
    usuario = db.relationship('Usuario', backref='ventas')
    vendedor = db.relationship('Vendedor', backref='ventas')
    lote = db.relationship('Lote', backref='ventas')
    
    def __repr__(self):
        return f'<Venta {self.id} - {self.producto.nombre}>'


class Vendedor(db.Model):
    """Modelo para vendedores"""
    __tablename__ = 'vendedores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    telefono = db.Column(db.String(20))
    comision_porcentaje = db.Column(db.Float, default=0)  # Porcentaje de comisión
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Vendedor {self.nombre}>'


class Lote(db.Model):
    """Modelo para lotes preparados (mezclas de productos)"""
    __tablename__ = 'lotes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    cantidad_preparada = db.Column(db.Integer, nullable=False)  # Unidades preparadas
    cantidad_vendida = db.Column(db.Integer, default=0)  # Cuántas se vendieron
    costo_total = db.Column(db.Float, nullable=False)  # Costo de preparación
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_preparacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    usuario = db.relationship('Usuario', backref='lotes')
    ingredientes = db.relationship('IngredienteLote', cascade='all, delete-orphan', backref='lote')
    
    @property
    def cantidad_restante(self):
        return self.cantidad_preparada - self.cantidad_vendida
    
    def __repr__(self):
        return f'<Lote {self.nombre} - {self.cantidad_preparada} unidades>'


class IngredienteLote(db.Model):
    """Modelo para ingredientes usados en un lote"""
    __tablename__ = 'ingredientes_lote'
    
    id = db.Column(db.Integer, primary_key=True)
    lote_id = db.Column(db.Integer, db.ForeignKey('lotes.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad_usada = db.Column(db.Float, nullable=False)  # Cantidad consumida
    costo_unitario = db.Column(db.Float, nullable=False)
    
    # Relaciones
    producto = db.relationship('Producto', backref='usos_en_lotes')
    
    def __repr__(self):
        return f'<IngredienteLote {self.producto.nombre}>'
