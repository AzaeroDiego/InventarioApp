# 🚀 INSTRUCCIONES DE ACTUALIZACIÓN - VERSIÓN CON MEJORAS

## Cambios Implementados

### ✅ 1. **Sidebar Responsive en Móvil**
- El panel lateral ahora tiene un botón hamburguesa en dispositivos móviles
- Se cierra automáticamente al hacer clic en una opción
- Sin perder funcionalidad en escritorio

### ✅ 2. **Panel de Usuario Simplificado**
- Removido el email grande que ocupaba espacio
- Ahora muestra: "Conectado como [Nombre]"
- Mejor uso del espacio en móvil

### ✅ 3. **Columnas en Productos: "Se Vende"**
- Nuevo campo: **¿Se Vende?** (SI/NO)
- SI = Producto de venta (aparece en nueva_venta)
- NO = Es ingrediente para lotes (aparece en nuevo_lote)
- Nueva columna en tabla de productos

### ✅ 4. **Filtros Inteligentes**
- **Nueva Venta**: Solo muestra productos con "Se Vende = SI"
- **Nuevo Lote**: Solo muestra ingredientes con "Se Vende = NO"
- Evita errores de lógica de negocio

### ✅ 5. **Zona Horaria Perú (UTC-5)**
- Configuración en `config.py`
- Las fechas de ventas ya no tendrán desfase de 6-8 horas
- Requiere actualizar datetimes en próximas versiones

### ✅ 6. **Scripts de Migración y Backup**
- `migrate_db.py`: Agrega columna sin perder datos
- `backup_restore.py`: Exporta/importa datos en JSON

---

## 🔧 PASOS PARA APLICAR EN PYTHONANYWHERE

### PASO 1: Descarga los cambios
```bash
cd /home/azaerodiego/InventarioApp
```

### PASO 2: Migrar Base de Datos
```bash
python migrate_db.py
```
**Esto agregará la columna 'se_vende' sin perder ninguna venta ni datos existentes.**

### PASO 3: Hacer Backup (Recomendado)
```bash
python backup_restore.py export
```
Esto creará una carpeta `backups/` con todos tus datos.

### PASO 4: Recargar la aplicación
En PythonAnywhere:
1. Vas a Web
2. Haces clic en "Reload" junto a tu app
3. Esperas 1 minuto

### PASO 5: Configurar Productos
En la aplicación:
1. Ve a **Editar Productos** (Admin)
2. Para cada producto, selecciona:
   - ✅ **SI**: Si es un producto que VENDES (Rebelde, Party Box, etc.)
   - ❌ **NO**: Si es un INGREDIENTE para lotes (Alcohol, Refrescos, etc.)
3. Guarda cambios

---

## 📱 PRUEBAS EN MÓVIL

### Sidebar Hamburguesa
```
Visible solo en pantalla < 768px
- Botón ≡ arriba a la izquierda
- Click abre menú lateral
- Click en link cierra automaticamente
- Click en fondo gris tb cierra
```

### Panel de Usuario
```
Antes: "Nombre Completo" + "email@example.com" (ocupaba espacio)
Ahora: "Conectado como Diego" (compacto)
```

### Nueva Venta
```
Lista desplegable SOLO muestra:
✅ Rebelde Paquete
✅ Party Box Lata
✅ Party Box 3L
❌ Pisco (NO aparece si está marcado NO)
```

### Nuevo Lote
```
Ingredientes Lista SOLO muestra:
❌ Alcohol (SI está marcado NO)
❌ Refrescos (SI está marcado NO)
✅ Otros ingredientes
```

---

## ⏰ ZONA HORARIA

**Antes**: Horas adelantadas (España UTC+2)
**Ahora**: Horas correctas de Perú (UTC-5)

Ejemplo:
```
Antes: 14:00 (mostraba hora de España)
Ahora: 08:00 (hora correcta de Perú)
```

---

## 💾 RECUPERACIÓN DE DATOS

Si necesitas restaurar datos de una exportación anterior:

```bash
python backup_restore.py import backups/backup_YYYYMMDD_HHMMSS.json
```

**Nota**: El script solo exporta datos de visibilidad, no reemplaza la BD.
Para cambiar datos online, debes editarlos manualmente en la interfaz.

---

## 🔍 VER CAMBIOS EN CÓDIGO

### Archivos Modificados:
- `app/models.py` - Agregada columna `se_vende`
- `app/main.py` - Filtros en nueva_venta y nuevo_lote
- `config.py` - Zona horaria
- `app/utils.py` - Función get_current_time()
- `templates/base.html` - Menú hamburguesa y JS
- `static/css/style.css` - Estilos responsive
- `templates/main/productos.html` - Nueva columna
- `templates/main/crear_producto.html` - Campo se_vende
- `templates/main/editar_producto.html` - Campo se_vende

### Archivos Nuevos:
- `migrate_db.py` - Script de migración
- `backup_restore.py` - Script de backup/restore

---

## ❓ PROBLEMAS COMUNES

### "Columna 'se_vende' no existe"
**Solución**: Ejecuta `python migrate_db.py`

### "Las horas siguen adelantadas"
**Solución**: Las NUEVAS ventas usarán hora correcta.
Las antiguas mantendrán su hora original (para auditoría).

### Sidebar no muestra en móvil
**Solución**: Recarga la página (Ctrl+F5 o Cmd+Shift+R)

### "Producto no aparece en Nueva Venta"
**Solución**: Ve a Editar ese Producto y marca "¿Se Vende? = SI"

---

## 📞 SOPORTE

Si encuentras problemas:
1. Verifica que ejecutaste `migrate_db.py`
2. Recarga la página (fuerza el caché del navegador)
3. Revisa la consola del navegador (F12)
4. Exporta un backup por si acaso

---

**¡Listo! Tu aplicación está actualizada. 🎉**
