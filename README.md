# Sistema de Gestión de Inventario
Sistema web moderno de gestión de inventario para pequeños negocios, desarrollado con Flask y SQLAlchemy.

## 📋 Características

✅ **Autenticación segura** con email y contraseña
✅ **Dashboard** con métricas en tiempo real
✅ **CRUD completo** de productos y categorías
✅ **Gestión de stock** con entradas y salidas
✅ **Alertas automáticas** de bajo stock
✅ **Códigos QR** por producto
✅ **Reportes y gráficos** interactivos
✅ **Exportación a CSV** de datos
✅ **Interfaz responsiva** y moderna
✅ **Interfaz completamente en español**

## 🛠️ Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes)
- Navegador web moderno

## 📦 Instalación

### 1. Clonar o descargar el proyecto
```bash
cd InventarioApp
```

### 2. Crear entorno virtual
```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Inicializar base de datos
```bash
# Crear base de datos con datos iniciales
python -c "from run import app; app.cli.invoke(('init-db',))"

# O usando Flask CLI
flask init-db
```

### 5. Crear usuario de prueba
```bash
python -c "from run import app; app.cli.invoke(('create-user',))"

# O usando Flask CLI
flask create-user
```

### 6. Ejecutar la aplicación
```bash
python run.py
```

La aplicación estará disponible en: **http://localhost:5000**

## 👤 Datos de Prueba

### Usuario Demo
- **Email:** demo@example.com
- **Contraseña:** 123456

### Productos Iniciales
1. **Rebelde Paquete** - Cerveza en paquete
2. **Party Box Lata** - Bebida energética en lata
3. **Party Box 3L** - Bebida energética en botellón
4. **Pisco** - Bebida alcohólica (750ml)

### Categorías Iniciales
- Bebidas Alcohólicas (Rojo)
- Bebidas No Alcohólicas (Azul)
- Snacks (Naranja)
- Otros (Gris)

## 📱 Estructura del Proyecto

```
InventarioApp/
├── app/
│   ├── __init__.py          # Inicialización de Flask
│   ├── models.py            # Modelos de base de datos
│   ├── auth.py              # Rutas de autenticación
│   ├── main.py              # Rutas principales
│   ├── api.py               # API Routes
│   └── utils.py             # Funciones auxiliares
├── templates/
│   ├── base.html            # Template base de la app
│   ├── auth_base.html       # Template base de autenticación
│   ├── auth/
│   │   ├── login.html       # Página de login
│   │   └── registro.html    # Página de registro
│   └── main/
│       ├── dashboard.html   # Panel principal
│       ├── productos.html   # Lista de productos
│       ├── categorias.html  # Gestión de categorías
│       ├── entrada_stock.html
│       ├── salida_stock.html
│       ├── movimientos_stock.html
│       ├── alertas.html
│       └── reportes.html
├── static/
│   ├── css/
│   │   └── style.css        # Estilos principales
│   ├── js/                  # Archivos JavaScript
│   ├── uploads/             # Imágenes de productos
│   └── qrcodes/             # Códigos QR generados
├── config.py                # Configuración de la aplicación
├── run.py                   # Punto de entrada
├── requirements.txt         # Dependencias
└── inventario.db            # Base de datos SQLite

```

## 🎯 Funcionalidades Principales

### 1. Dashboard
- Total de productos
- Productos con bajo stock
- Valor total del inventario
- Alertas sin leer
- Historial de actividad reciente

### 2. Gestión de Productos
- Ver lista completa de productos
- Crear nuevos productos
- Editar información
- Eliminar (desactivar) productos
- Asignar categorías
- Subir imágenes
- Generar códigos QR automáticos

### 3. Categorías
- Crear nuevas categorías
- Asignar colores personalizados
- Ver productos por categoría

### 4. Stock
- Registrar entradas de stock
- Registrar salidas de stock
- Ver historial completo de movimientos
- Filtrar por tipo de movimiento
- Exportar historial

### 5. Alertas
- Alertas automáticas de bajo stock
- Notificaciones en tiempo real
- Acceso rápido a registrar entrada

### 6. Reportes
- Productos más vendidos (gráficos)
- Valor por categoría (gráficos)
- Movimientos de los últimos 30 días
- Exportar datos a CSV

## 🔧 Configuración

Editar `config.py` para personalizar:
- Ruta de base de datos
- Claves secretas
- Tamaño máximo de archivos
- Rutas de subidas

## 🔐 Seguridad

- Contraseñas encriptadas con Werkzeug
- Protección CSRF en formularios
- Autenticación requerida para todas las vistas
- Session cookies seguras
- Validación de entrada en todos los formularios

## 🚀 Deployment

### Para producción:
1. Cambiar `DEBUG = False` en config.py
2. Generar nueva `SECRET_KEY`
3. Usar servidor WSGI (Gunicorn, uWSGI)
4. Implementar HTTPS
5. Usar base de datos PostgreSQL

```bash
# Ejemplo con Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## 📝 Base de Datos

La aplicación utiliza SQLite por defecto (ideal para desarrollo y pequeñas implementaciones).

Para cambiar a PostgreSQL, modificar en `config.py`:
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/inventario'
```

## 🤝 Contribuciones

Este proyecto fue creado como plantilla para pequeños negocios que necesitan gestionar su inventario de forma sencilla.

## 📄 Licencia

Uso libre para propósitos comerciales y personales.

## 🆘 Soporte

En caso de problemas:
1. Verificar que Python 3.8+ está instalado
2. Confirmar que todas las dependencias están instaladas
3. Eliminar `inventario.db` y ejecutar `flask init-db` nuevamente
4. Revisar los logs de error en la consola

## 🔄 Actualizar Dependencias

```bash
pip install --upgrade -r requirements.txt
```

---

**Desarrollado con ❤️ para pequeños negocios**
