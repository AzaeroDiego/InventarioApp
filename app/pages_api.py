"""Authenticated JSON boundary for the independently hosted GitHub Pages UI."""
from functools import wraps
from math import isfinite
from datetime import datetime, time, timedelta, timezone
from flask import Blueprint, current_app, request, jsonify, g, send_from_directory
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from sqlalchemy import update, func, case, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask_login import login_user
from app import db
from app.models import Usuario, Producto, Categoria, MovimientoStock, Venta, AlertaStock

pages_bp = Blueprint('pages', __name__)


def signer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='pages-access-v1')


@pages_bp.before_request
def preflight():
    if request.path.startswith('/api/pages/') and request.method == 'OPTIONS':
        return '', 204


@pages_bp.after_request
def cors(response):
    if request.path.startswith('/api/pages/'):
        origin = request.headers.get('Origin')
        allowed = current_app.config.get('PAGES_ORIGIN', '').rstrip('/')
        if origin and origin == allowed:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.vary.add('Origin')
        response.headers['Cache-Control'] = 'no-store'
    return response


def authenticated(write=False):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            token = request.headers.get('Authorization', '').removeprefix('Bearer ')
            try:
                payload = signer().loads(token, max_age=28800)
                g.pages_user = db.session.get(Usuario, payload['uid'])
            except (BadSignature, SignatureExpired, KeyError, TypeError):
                return jsonify(error='Tu sesión ha caducado. Vuelve a iniciar sesión.'), 401
            if not g.pages_user or not g.pages_user.activo:
                return jsonify(error='Usuario no disponible.'), 401
            if write and not g.pages_user.has_permisos:
                return jsonify(error='Tu cuenta tiene acceso de solo lectura.'), 403
            return fn(*args, **kwargs)
        return wrapped
    return decorator


@pages_bp.route('/workspace/')
def workspace():
    return send_from_directory('../web', 'index.html')


@pages_bp.route('/workspace/<path:asset>')
def workspace_asset(asset):
    return send_from_directory('../web', asset)


@pages_bp.route('/api/pages/health')
def health():
    return jsonify(status='ok')


LEGACY_TARGETS = {
    'control-barra': '/barra', 'lotes': '/lotes', 'vendedores': '/vendedores',
    'categorias': '/categorias', 'usuarios': '/admin/usuarios', 'reportes': '/reportes'
}


@pages_bp.route('/api/pages/launch', methods=['POST'])
@authenticated()
def launch():
    target = (request.get_json(silent=True) or {}).get('target')
    if target not in LEGACY_TARGETS:
        return jsonify(error='Destino no válido.'), 400
    ticket = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='pages-launch-v1').dumps(
        {'uid': g.pages_user.id, 'target': target})
    return jsonify(ticket=ticket)


@pages_bp.route('/api/pages/launch-session', methods=['POST'])
def launch_session():
    from flask import redirect
    try:
        payload = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='pages-launch-v1').loads(
            request.form.get('ticket', ''), max_age=30)
        user = db.session.get(Usuario, payload['uid'])
        destination = LEGACY_TARGETS[payload['target']]
        if not user or not user.activo:
            raise ValueError()
    except (BadSignature, SignatureExpired, KeyError, TypeError, ValueError):
        return 'El enlace de acceso caducó. Vuelve a abrirlo desde tu inventario.', 401
    login_user(user, remember=False)
    return redirect(destination, code=303)


@pages_bp.route('/api/pages/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))
    user = Usuario.query.filter_by(email=email).first()
    # Always verify a hash to reduce account enumeration through timing.
    from werkzeug.security import check_password_hash
    valid = user.check_password(password) if user else check_password_hash(
        'scrypt:32768:8:1$pagesdummy$' + '0' * 128, password)
    if not user or not valid or not user.activo:
        return jsonify(error='Correo o contraseña incorrectos.'), 401
    return jsonify(token=signer().dumps({'uid': user.id}), user={
        'nombre': user.nombre_completo, 'write': bool(user.has_permisos)})


@pages_bp.route('/api/pages/data')
@authenticated()
def data():
    products = Producto.query.options(joinedload(Producto.categoria)).filter_by(activo=True).order_by(Producto.nombre).all()
    movements = MovimientoStock.query.options(joinedload(MovimientoStock.producto), joinedload(MovimientoStock.usuario)).order_by(MovimientoStock.fecha.desc()).limit(500).all()
    sales = Venta.query.options(joinedload(Venta.producto)).order_by(Venta.fecha.desc()).limit(500).all()
    tz = current_app.config['TIMEZONE']
    today = datetime.now(tz).date()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    starts = [tz.localize(datetime.combine(day, time.min)).astimezone(timezone.utc).replace(tzinfo=None) for day in days]
    totals = db.session.query(*[func.coalesce(func.sum(case((
        and_(Venta.fecha >= start, Venta.fecha < start + timedelta(days=1)), Venta.total),
        else_=0)), 0) for start in starts]).filter(Venta.fecha >= starts[0]).one()
    return jsonify(
        products=[dict(id=p.id, nombre=p.nombre, sku=p.sku, categoria=p.categoria.nombre,
                       categoria_id=p.categoria_id, precio=p.precio, stock=p.cantidad_stock,
                       minimo=p.stock_minimo, se_vende=p.se_vende) for p in products],
        categories=[dict(id=c.id, nombre=c.nombre) for c in Categoria.query.filter_by(activa=True).all()],
        movements=[dict(id=m.id, producto=m.producto.nombre, tipo=m.tipo, cantidad=m.cantidad,
                        motivo=m.motivo, fecha=m.fecha.isoformat()+'Z', usuario=m.usuario.nombre_completo) for m in movements],
        sales=[dict(id=v.id, producto=v.producto.nombre, cantidad=v.cantidad, total=v.total,
                    fecha=v.fecha.isoformat()+'Z') for v in sales],
        history_limit=500,
        daily_sales=[dict(day=day.isoformat(), total=float(total)) for day, total in zip(days, totals)],
        user=dict(nombre=g.pages_user.nombre_completo, write=bool(g.pages_user.has_permisos)))


@pages_bp.route('/api/pages/products', methods=['POST'])
@authenticated(write=True)
def create_product():
    data = request.get_json(silent=True) or {}
    try:
        name, sku = str(data.get('nombre', '')).strip(), str(data.get('sku', '')).strip()
        price, minimum = float(data['precio']), int(data['minimo'])
        category = db.session.get(Categoria, int(data['categoria_id']))
        if not name or len(name) > 150 or not sku or len(sku) > 50 or not category or not category.activa or not isfinite(price) or price < 0 or minimum < 0:
            raise ValueError()
        db.session.add(Producto(nombre=name, sku=sku, categoria_id=category.id, precio=price,
                                stock_minimo=minimum, cantidad_stock=0, se_vende=bool(data.get('se_vende', True))))
        db.session.commit()
        return jsonify(ok=True), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify(error='Ese SKU ya existe.'), 409
    except (ValueError, TypeError, KeyError, OverflowError):
        db.session.rollback()
        return jsonify(error='Revisa el nombre, SKU, categoría, precio y stock mínimo.'), 400


@pages_bp.route('/api/pages/movements', methods=['POST'])
@authenticated(write=True)
def create_movement():
    data = request.get_json(silent=True) or {}
    try:
        amount = int(data['cantidad'])
        if isinstance(data['cantidad'], bool) or str(amount) != str(data['cantidad']) or amount <= 0:
            raise ValueError()
        kind = data['tipo']
        if kind not in ('entrada', 'salida', 'venta'):
            raise ValueError()
        product_id = int(data['producto_id'])
        price = float(data.get('precio', 0))
        if not isfinite(price) or price < 0:
            raise ValueError()
        product = db.session.get(Producto, product_id)
        if not product or not product.activo or (kind == 'venta' and not product.se_vende):
            raise ValueError()
        stmt = update(Producto).where(Producto.id == product_id, Producto.activo == True)
        if kind != 'entrada':
            stmt = stmt.where(Producto.cantidad_stock >= amount)
        result = db.session.execute(stmt.values(cantidad_stock=Producto.cantidad_stock + (amount if kind == 'entrada' else -amount)))
        if result.rowcount != 1:
            db.session.rollback()
            return jsonify(error='Stock insuficiente. Actualiza el inventario.'), 409
        reason = str(data.get('motivo', '')).strip()[:200] or ('Venta' if kind == 'venta' else 'Movimiento de stock')
        db.session.add(MovimientoStock(producto_id=product_id, usuario_id=g.pages_user.id,
            tipo='entrada' if kind == 'entrada' else 'salida', cantidad=amount, motivo=reason))
        if kind == 'venta':
            db.session.add(Venta(producto_id=product_id, usuario_id=g.pages_user.id,
                cantidad=amount, precio_unitario=price, total=amount*price, motivo='Venta normal'))
        db.session.refresh(product)
        if product.cantidad_stock < product.stock_minimo and not AlertaStock.query.filter_by(producto_id=product_id, leida=False).first():
            db.session.add(AlertaStock(producto_id=product_id, mensaje=f'{product.nombre} por debajo del stock mínimo'))
        db.session.commit()
        return jsonify(ok=True), 201
    except (ValueError, TypeError, KeyError, OverflowError):
        db.session.rollback()
        return jsonify(error='Revisa el producto, la cantidad y el precio.'), 400
