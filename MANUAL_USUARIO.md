# Manual de Usuario - Sistema de Gestión de Inventario

## 📖 Índice
1. Primeros pasos
2. Dashboard
3. Gestión de Productos
4. Gestión de Stock
5. Reportes y Alertas
6. Códigos QR
7. Tips y Trucos

---

## 1️⃣ Primeros Pasos

### Registro de Cuenta
1. Accede a **http://localhost:5000**
2. Haz clic en "Regístrate aquí"
3. Completa el formulario:
   - Nombre completo
   - Email
   - Contraseña (mínimo 6 caracteres)
4. Confirma la contraseña
5. Haz clic en "Registrarse"

### Iniciar Sesión
1. Ingresa tu email
2. Ingresa tu contraseña
3. Marca "Recuérdame" si lo deseas
4. Haz clic en "Iniciar Sesión"

---

## 2️⃣ Dashboard

El panel principal te muestra:
- **Total de Productos**: Cantidad de artículos en el sistema
- **Productos con Bajo Stock**: Rojo = necesitan reabastecimiento
- **Valor del Inventario**: Valor total monetario
- **Alertas**: Notificaciones importantes
- **Actividad Reciente**: Últimas transacciones

### Acciones Rápidas
- "Gestionar Productos" → Ir a lista completa
- "Ver Reportes" → Análisis y gráficos

---

## 3️⃣ Gestión de Productos

### Crear Producto
1. En el sidebar, haz clic en **"Productos"**
2. Haz clic en **"+ Nuevo Producto"**
3. Completa los datos:
   - **Nombre**: Nombre del producto (Ej: "Rebelde Paquete")
   - **SKU**: Código único (Ej: "REB-PKG")
   - **Categoría**: Selecciona o crea una
   - **Precio**: Precio unitario
   - **Stock Inicial**: Cantidad disponible
   - **Stock Mínimo**: Nivel de alerta (Ej: 10)
   - **Imagen**: Sube una foto (opcional)
4. Haz clic en **"Crear Producto"**

Sistema genera automáticamente un código QR

### Editar Producto
1. En la lista de productos
2. Haz clic en el botón **"✏️ Editar"**
3. Modifica los datos necesarios
4. Haz clic en **"Guardar Cambios"**

### Buscar / Filtrar
1. En la lista de productos
2. **Buscador**: Ingresa nombre o SKU
3. **Categoría**: Filtra por tipo
4. **Estado**: Todos / Bajo Stock / Sin Stock
5. Haz clic en **"Buscar"**

---

## 4️⃣ Gestión de Stock

### Registrar Entrada (Compra/Recepción)
1. En el sidebar → **"Entrada de Stock"**
2. Selecciona el **Producto**
3. Ingresa la **Cantidad**
4. Selecciona el **Motivo**:
   - Compra
   - Devolución de cliente
   - Ajuste inventario
   - Producción
5. Haz clic en **"Registrar Entrada"**

### Registrar Salida (Venta/Uso)
1. En el sidebar → **"Salida de Stock"**
2. Selecciona el **Producto**
   - Verás el stock disponible
3. Ingresa la **Cantidad**
   - Sistema previene sobre-venta
4. Selecciona el **Motivo**:
   - Venta
   - Pérdida/Rotura
   - Ajuste inventario
   - Devolución a proveedor
5. Haz clic en **"Registrar Salida"**

### Ver Historial
1. En el sidebar → **"Historial"**
2. Filtra por:
   - Tipo de movimiento
   - Producto específico
3. Visualiza fecha, usuario y cantidad

---

## 5️⃣ Categorías

### Crear Categoría
1. En el sidebar → **"Categorías"**
2. Haz clic en **"+ Nueva Categoría"**
3. Ingresa:
   - **Nombre**: (Ej: "Bebidas Alcohólicas")
   - **Color**: Selecciona un color
4. Haz clic en **"Crear Categoría"**

### Editar Categoría
1. En la lista de categorías
2. Haz clic en **"Editar"**
3. Modifica nombre y/o color
4. Haz clic en **"Guardar Cambios"**

---

## 6️⃣ Alertas

### Alertas Automáticas
Cuando el stock de un producto cae por debajo del nivel mínimo:
- Aparece una alerta en rojo
- Se genera notificación en el sidebar
- Aparece un badge con el número

### Ver Alertas
1. En el sidebar → **"Alertas"** (con número rojo si hay)
2. Verás lista de productos afectados
3. Haz clic en **"Entrada"** para reabastecerse

---

## 7️⃣ Códigos QR

### Ver Código QR
1. En la lista de productos
2. Haz clic en el icono **"QR"** (cuadrado con líneas)
3. Se abre ventana con el código

### Descargar QR
1. En la ventana del código QR
2. Haz clic en **"Descargar"**
3. Se descarga como PNG

### Imprimir QR
1. En la ventana del código QR
2. Haz clic en **"Imprimir"**
3. Sistema abre diálogo de impresión

### Usar Código QR
- Pega el código en etiquetas de producto
- Escanea con cualquier lector QR
- Contiene: SKU, nombre e ID del producto

---

## 8️⃣ Reportes

### Acceder
1. En el sidebar → **"Reportes"**
2. Verás tres gráficos interactivos:
   - **Productos Más Vendidos**: Dona
   - **Valor por Categoría**: Barras
   - **Movimientos (30 días)**: Línea

### Exportar Datos
1. En la parte superior de reportes
2. Haz clic en:
   - **"Exportar Productos (CSV)"** - Lista completa
   - **"Exportar Movimientos (CSV)"** - Historial completo

3. El archivo se descarga automáticamente
4. Abre en Excel o similar

---

## 💡 Tips y Trucos

### Buscador Inteligente
- Busca por nombre: "Rebelde"
- Busca por SKU: "REB-PKG"
- Búsqueda parcial funciona

### Stock Mínimo
- Recomendación: 2 semanas de venta
- Para producto vendido 10x/semana: stock min = 20
- Se revisa automáticamente en cada salida

### Filtros Combinados
- Puedes aplicar múltiples filtros a la vez
- Categoría + Estado + Búsqueda = resultados precisos

### Exportar para Contabilidad
1. Exporta movimientos con fecha
2. Abre en Excel
3. Haz cálculo de COGS (Costo de Ventas)

### Hacer Backup
1. Localiza el archivo `inventario.db`
2. Copia a ubicación segura
3. ¡Protegido!

### Cambiar Contraseña
- De momento: crear nueva cuenta y deleter la anterior
- Próxima versión: opción en perfil

---

## ⚡ Atajos del Teclado

| Atajo | Acción |
|-------|--------|
| `Tab` | Navega entre campos |
| `Enter` | Envía formulario |
| `Esc` | Cierra modales |

---

## 🆘 Preguntas Frecuentes

### P: ¿Puedo editar una salida ya registrada?
**R:** No, por seguridad. Debes crear una entrada de corrección.

### P: ¿Qué pasa si vendo más del stock?
**R:** El sistema lo previene. No puedes registrar una salida sin stock.

### P: ¿Puedo eliminar un producto?
**R:** Sí, se marca como inactivo (no se borra, para auditoría).

### P: ¿Dónde están mis imágenes?
**R:** En la carpeta `/static/uploads/`

### P: ¿Cada cuánto se actualiza el dashboard?
**R:** En tiempo real. Las alertas cada 30 segundos.

---

## 📞 Soporte

En caso de problemas:
1. Verifica que el servidor esté corriendo
2. Intenta refresco de página (F5)
3. Limpia caché del navegador
4. Revisa la consola de desarrollador (F12)

---

**¡Que disfrutes usando tu Sistema de Inventario! 📦**
