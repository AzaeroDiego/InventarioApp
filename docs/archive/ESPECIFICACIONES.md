# Especificaciones Técnicas - Sistema de Inventario

## 📊 Base de Datos

### Tablas Principales

#### usuarios
- `id`: Identificador único (PK)
- `nombre_completo`: Nombre del usuario
- `email`: Email único para login
- `password_hash`: Contraseña encriptada
- `activo`: Estado del usuario
- `fecha_creacion`: Timestamp de creación

#### categorias
- `id`: Identificador único (PK)
- `nombre`: Nombre categoría (único)
- `color`: Color hex (#RRGGBB)
- `descripcion`: Descripción opcional
- `activa`: Estado de la categoría
- `fecha_creacion`: Timestamp

#### productos
- `id`: Identificador único (PK)
- `nombre`: Nombre del producto
- `sku`: Código único del producto
- `categoria_id`: FK a categorías
- `descripcion`: Descripción detallada
- `precio`: Precio unitario
- `cantidad_stock`: Stock actual
- `stock_minimo`: Nivel de alerta
- `imagen_url`: Ruta de imagen
- `codigo_qr`: Ruta del código QR
- `activo`: Estado del producto
- `fecha_creacion`: Timestamp
- `fecha_actualizacion`: Última modificación

#### movimientos_stock
- `id`: Identificador único (PK)
- `producto_id`: FK a productos
- `usuario_id`: FK a usuarios
- `tipo`: (entrada, salida, ajuste, devolución, corrección)
- `cantidad`: Cantidad movida
- `motivo`: Razón del movimiento
- `observaciones`: Notas adicionales
- `fecha`: Timestamp del movimiento

#### alertas_stock
- `id`: Identificador único (PK)
- `producto_id`: FK a productos
- `tipo`: Tipo de alerta (bajo_stock)
- `mensaje`: Descripción de la alerta
- `leida`: Estado de lectura
- `fecha_creacion`: Timestamp

## 🔌 API Endpoints

### Autenticación
- `POST /auth/login` - Iniciar sesión
- `POST /auth/registro` - Registrar usuario
- `GET /auth/logout` - Cerrar sesión

### Dashboard
- `GET /dashboard` - Panel principal

### Productos
- `GET /productos` - Listar productos (con filtros)
- `GET /producto/nuevo` - Formulario crear producto
- `POST /producto/nuevo` - Crear producto
- `GET /producto/<id>/editar` - Formulario editar
- `POST /producto/<id>/editar` - Guardar cambios
- `POST /producto/<id>/eliminar` - Eliminar producto

### Categorías
- `GET /categorias` - Listar categorías
- `GET /categoria/nueva` - Formulario crear
- `POST /categoria/nueva` - Crear categoría
- `GET /categoria/<id>/editar` - Formulario editar
- `POST /categoria/<id>/editar` - Guardar cambios

### Stock
- `GET /stock/movimientos` - Historial movimientos
- `GET /stock/entrada` - Formulario entrada
- `POST /stock/entrada` - Registrar entrada
- `GET /stock/salida` - Formulario salida
- `POST /stock/salida` - Registrar salida

### Reportes
- `GET /reportes` - Página de reportes
- `GET /alertas` - Listar alertas

### API REST
- `GET /api/alertas/no-leidas` - Alertas sin leer (JSON)
- `GET /api/producto/<id>/qr` - Código QR (JSON)
- `GET /api/reportes/exportar-csv?tipo=productos` - CSV productos
- `GET /api/reportes/exportar-csv?tipo=movimientos` - CSV movimientos
- `GET /api/estadisticas` - Estadísticas (JSON)

## 🎨 Paleta de Colores

```css
--primary: #2ecc71        /* Verde principal */
--primary-dark: #27ae60   /* Verde oscuro */
--secondary: #3498db      /* Azul */
--danger: #e74c3c         /* Rojo */
--warning: #f39c12        /* Naranja */
--success: #2ecc71        /* Verde */
--info: #3498db           /* Azul info */
--dark: #2c3e50           /* Gris oscuro */
--text: #34495e           /* Texto gris */
--light: #ecf0f1          /* Gris claro */
```

## 📱 Responsive Breakpoints

- Desktop: > 1024px (sin cambios)
- Tablet: 768px - 1024px (ajustes de layout)
- Mobile: < 768px (sidebar adaptado)
- Small Mobile: < 480px (textos más pequeños)

## 📦 Dependencias

```
Flask==2.3.2                 # Framework web
Flask-SQLAlchemy==3.0.5      # ORM
Flask-Login==0.6.2           # Autenticación
Flask-WTF==1.1.1             # Formularios web
WTForms==3.0.1               # Validación formularios
Werkzeug==2.3.6              # Utilidades seguridad
python-dotenv==1.0.0         # Variables entorno
qrcode==7.4.2                # Generación QR
Pillow==10.0.0               # Procesamiento imágenes
pandas==2.0.3                # Análisis datos
openpyxl==3.1.2              # Excel (futuro)
```

## 🔐 Seguridad Implementada

✅ Encriptación de contraseñas con Werkzeug
✅ Protección CSRF en formularios
✅ Validación de input en servidor y cliente
✅ Sesiones seguras con HttpOnly cookies
✅ SQL Injection prevención (SQLAlchemy)
✅ File upload validation
✅ Rate limiting (para implementar)

## ⚡ Performance

- Paginación de 20 items por página
- Índices en: SKU, email, fecha
- Lazy loading de relaciones
- Cache de alertas (30 segundos)
- Compresión de imágenes (futuro)

## 🐛 Error Handling

- Try-catch global en rutas
- Validación de formularios frontend y backend
- Mensajes de error amigables al usuario
- Logging de errores en consola

## 📋 Validaciones

### Productos
- Nombre: requerido, max 150 chars
- SKU: requerido, único, max 50 chars
- Precio: > 0
- Stock: >= 0
- categoría: requerida

### Usuario
- Email: formato válido, único
- Contraseña: min 6 caracteres
- Nombre: requerido

### Movimientos
- Cantidad: > 0
- Producto: requerido
- Stock suficiente para salidas

## 📊 Funcionalidades Gráficas

### Chart.js 3.9.1
- Gráfico de dona: Productos más vendidos
- Gráfico de barras: Valor por categoría
- Gráfico de línea: Movimientos 30 días

## 🌍 Internacionalización

- Interfaz: Español (es-CL)
- Fechas: DD/MM/YYYY HH:MM:SS
- Moneda: $ (Se puede personalizar)
- Números: , para decimales

## 🔄 Procesos Automatizados

1. **Generación QR**: Al crear producto
2. **Alertas**: Al hacer salida si stock < mínimo
3. **Auditoría**: Cada movimiento registra usuario y fecha
4. **Validación**: Prevención de incoherencias

## 📈 Métricas Disponibles

- Total de productos activos
- Productos con bajo stock
- Productos sin stock
- Valor total del inventario
- Entradas en últimos X días
- Salidas en últimos X días
- Productos más vendidos
- Valor por categoría

## 🚀 Hoja de Ruta Futura

- [ ] Integración con códigos de barras
- [ ] Exportación a Excel con formato
- [ ] Gráficos interactivos mejorados
- [ ] Notificaciones por email
- [ ] Integración con proveedores
- [ ] Sistema de compras automáticas
- [ ] Análisis de pronóstico
- [ ] App móvil
- [ ] Multiusuario con permisos
- [ ] Integración con sistemas POS

