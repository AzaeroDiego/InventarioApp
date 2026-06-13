from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy import desc, func

from app import db
from app.models import Usuario


barra_bp = Blueprint('barra', __name__)


CATALOGO_BARRA = [
    {'producto': 'Cerveza', 'precio': 15.00},
    {'producto': 'Corona', 'precio': 15.00},
    {'producto': 'Four loco', 'precio': 15.00},
    {'producto': "Mike's", 'precio': 12.00},
    {'producto': 'Smirnoff', 'precio': 90.00},
    {'producto': 'Ruskaya', 'precio': 0.00},
    {'producto': 'Wisky Red label', 'precio': 150.00},
    {'producto': 'Wisky Black label', 'precio': 200.00},
    {'producto': 'old time', 'precio': 80.00},
    {'producto': 'Ron Cabo Blanco', 'precio': 50.00},
    {'producto': 'agua', 'precio': 4.00},
    {'producto': 'guaraná pequeña', 'precio': 5.00},
    {'producto': 'guaraná grande', 'precio': 20.00},
    {'producto': 'pepsi', 'precio': 5.00},
    {'producto': 'coca cola', 'precio': 6.00},
    {'producto': 'cusqueña pequeña', 'precio': 12.00},
    {'producto': 'Cigarro', 'precio': 2.50},
    {'producto': 'Ron cartavio', 'precio': 90.00},
    {'producto': 'Pisco Sour', 'precio': 25.00},
    {'producto': 'Margarita Corona', 'precio': 25.00},
    {'producto': 'Mojito', 'precio': 40.00},
    {'producto': 'Copa Pisco Sour', 'precio': 23.00},
    {'producto': 'Sangría', 'precio': 15.00},
]

CATALOGO_BARRA_MAP = {item['producto']: item for item in CATALOGO_BARRA}


class ControlBarra(db.Model):
    """Cabecera del control de barra por turno o cierre."""
    __tablename__ = 'controles_barra'

    id = db.Column(db.Integer, primary_key=True)
    fecha_operacion = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    hora_cierre = db.Column(db.String(20))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    responsable_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    observaciones = db.Column(db.Text)
    total_esperado = db.Column(db.Float, nullable=False, default=0)
    monto_entregado = db.Column(db.Float, nullable=False, default=0)
    diferencia_caja = db.Column(db.Float, nullable=False, default=0)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    usuario = db.relationship('Usuario', foreign_keys=[usuario_id], backref='controles_barra_registrados')
    responsable = db.relationship('Usuario', foreign_keys=[responsable_id], backref='controles_barra_responsable')
    detalles = db.relationship('DetalleControlBarra', backref='control', lazy=True, cascade='all, delete-orphan')

    def recalcular_totales(self):
        self.total_esperado = sum(detalle.total_esperado for detalle in self.detalles)
        self.diferencia_caja = self.monto_entregado - self.total_esperado


class DetalleControlBarra(db.Model):
    """Detalle de productos contados en barra."""
    __tablename__ = 'detalle_controles_barra'

    id = db.Column(db.Integer, primary_key=True)
    control_id = db.Column(db.Integer, db.ForeignKey('controles_barra.id'), nullable=False)
    producto = db.Column(db.String(150), nullable=False)
    stock_inicial = db.Column(db.Integer, nullable=False, default=0)
    stock_final = db.Column(db.Integer, nullable=False, default=0)
    vendidos = db.Column(db.Integer, nullable=False, default=0)
    precio_unitario = db.Column(db.Float, nullable=False, default=0)
    total_esperado = db.Column(db.Float, nullable=False, default=0)

    def calcular(self):
        self.vendidos = self.stock_inicial - self.stock_final
        self.total_esperado = self.vendidos * self.precio_unitario


@barra_bp.route('/barra', methods=['GET', 'POST'])
@login_required
def control_barra():
    """Registrar y consultar cierres de barra independientes del inventario principal."""
    usuarios = Usuario.query.filter_by(activo=True).order_by(Usuario.nombre_completo).all()

    if request.method == 'POST':
        try:
            fecha_operacion_txt = request.form.get('fecha_operacion')
            hora_cierre = request.form.get('hora_cierre', '').strip()
            responsable_id = request.form.get('responsable_id', type=int)
            monto_entregado = request.form.get('monto_entregado', 0, type=float) or 0
            observaciones = request.form.get('observaciones', '').strip()

            productos = request.form.getlist('producto[]')
            stocks_iniciales = request.form.getlist('stock_inicial[]')
            stocks_finales = request.form.getlist('stock_final[]')
            precios = request.form.getlist('precio_unitario[]')

            if not responsable_id:
                flash('Selecciona el usuario responsable de la barra.', 'error')
                return redirect(url_for('barra.control_barra'))

            if not productos:
                flash('No se recibió el catálogo de productos de barra.', 'error')
                return redirect(url_for('barra.control_barra'))

            try:
                fecha_operacion = datetime.strptime(fecha_operacion_txt, '%Y-%m-%d').date() if fecha_operacion_txt else datetime.utcnow().date()
            except ValueError:
                flash('La fecha de operación no tiene un formato válido.', 'error')
                return redirect(url_for('barra.control_barra'))

            control = ControlBarra(
                fecha_operacion=fecha_operacion,
                hora_cierre=hora_cierre,
                usuario_id=current_user.id,
                responsable_id=responsable_id,
                monto_entregado=monto_entregado,
                observaciones=observaciones
            )

            for idx, nombre_producto in enumerate(productos):
                nombre_producto = (nombre_producto or '').strip()
                if nombre_producto not in CATALOGO_BARRA_MAP:
                    flash(f'Producto de barra no permitido: {nombre_producto}', 'error')
                    return redirect(url_for('barra.control_barra'))

                try:
                    stock_inicial = int(stocks_iniciales[idx] or 0)
                    stock_final = int(stocks_finales[idx] or 0)
                    precio_form = float(precios[idx] or 0)
                except (ValueError, IndexError):
                    flash(f'Revisa las cantidades del producto: {nombre_producto}', 'error')
                    return redirect(url_for('barra.control_barra'))

                precio_catalogo = float(CATALOGO_BARRA_MAP[nombre_producto]['precio'])
                precio_unitario = precio_catalogo if precio_catalogo > 0 else precio_form

                if stock_inicial < 0 or stock_final < 0 or precio_unitario < 0:
                    flash('No se permiten valores negativos en stock o precio.', 'error')
                    return redirect(url_for('barra.control_barra'))

                if stock_final > stock_inicial:
                    flash(f'El stock restante no puede ser mayor al stock inicial en: {nombre_producto}', 'error')
                    return redirect(url_for('barra.control_barra'))

                # Guardar solo productos que fueron contabilizados en la barra.
                if stock_inicial == 0 and stock_final == 0:
                    continue

                detalle = DetalleControlBarra(
                    producto=nombre_producto,
                    stock_inicial=stock_inicial,
                    stock_final=stock_final,
                    precio_unitario=precio_unitario
                )
                detalle.calcular()
                control.detalles.append(detalle)

            if not control.detalles:
                flash('Ingresa stock inicial o stock restante en al menos un producto de barra.', 'error')
                return redirect(url_for('barra.control_barra'))

            control.recalcular_totales()
            db.session.add(control)
            db.session.commit()

            flash('✅ Cierre de barra guardado correctamente.', 'success')
            return redirect(url_for('barra.control_barra'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar el cierre de barra: {str(e)}', 'error')
            return redirect(url_for('barra.control_barra'))

    controles = ControlBarra.query.order_by(desc(ControlBarra.fecha_creacion)).limit(20).all()
    total_dia = db.session.query(func.sum(ControlBarra.total_esperado)).filter(
        ControlBarra.fecha_operacion == datetime.utcnow().date()
    ).scalar() or 0

    return render_template(
        'main/control_barra.html',
        usuarios=usuarios,
        controles=controles,
        total_dia=total_dia,
        hoy=datetime.utcnow().date(),
        catalogo_barra=CATALOGO_BARRA
    )
