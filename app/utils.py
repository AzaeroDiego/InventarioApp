import os
import qrcode
from datetime import datetime
import pytz
from config import Config
from app.models import Producto
from app import db

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def get_current_time():
    """Obtener hora actual en la zona horaria de Perú"""
    utc_now = datetime.utcnow()
    utc_now = pytz.UTC.localize(utc_now)
    return utc_now.astimezone(Config.TIMEZONE)


def allowed_file(filename):
    """Verificar si la extensión del archivo es permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_qr(producto):
    """Generar código QR para un producto"""
    try:
        # Crear carpeta de QR si no existe
        qr_folder = os.path.join('static', 'qrcodes')
        if not os.path.exists(qr_folder):
            os.makedirs(qr_folder)
        
        # Datos del código QR
        qr_data = f"SKU:{producto.sku}|Nombre:{producto.nombre}|ID:{producto.id}"
        
        # Generar código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Crear imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Guardar imagen
        filename = f"{producto.sku}_{producto.id}.png"
        filepath = os.path.join(qr_folder, filename)
        img.save(filepath)
        
        # Actualizar ruta en la base de datos
        producto.codigo_qr = f'/static/qrcodes/{filename}'
        db.session.commit()
        
        return True
    except Exception as e:
        print(f"Error generando QR: {e}")
        return False


def get_formato_moneda(valor):
    """Formato de moneda en soles peruanos"""
    return f"S/ {valor:,.2f}".replace(',', '.')
