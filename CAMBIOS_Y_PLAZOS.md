# 📋 CAMBIOS REALIZADOS Y PLAZOS - SISTEMA DE GESTIÓN DE INVENTARIO

**Versión**: 2.1 - Actualización Móvil, Zona Horaria y Gestión de Usuarios  
**Fecha de Cambios**: 15 de Marzo de 2026  
**Ambiente**: PythonAnywhere (Producción)

---

## 📑 TABLA DE CONTENIDOS
1. [Cambios Implementados](#cambios-implementados)
2. [Plazos y Timeline](#plazos-y-timeline)
3. [Plan de BD](#plan-de-base-de-datos)
4. [Instrucciones de Despliegue](#instrucciones-de-despliegue)
5. [Rollback - En Caso de Error](#rollback---en-caso-de-error)

---

## 🔄 CAMBIOS IMPLEMENTADOS

### CAMBIO 1: Sidebar Responsive (Móvil)
**Estado**: ✅ COMPLETADO  
**Archivos Modificados**:
- `static/css/style.css` - Estilos responsive (@media queries)
- `templates/base.html` - Botón hamburguesa y JS de toggle
- `static/js/utils.js` (si existe) - Funciones de menú

**Descripción**:
- Sidebar se oculta en pantallas < 768px
- Botón hamburguesa (≡) aparece arriba a la izquierda
- Click abre/cierra menú con animación suave
- Overlay gris se cierra al hacer clic en links

**Impacto en BD**: ❌ Ninguno (solo CSS/JS)

---

### CAMBIO 2: Panel de Usuario Simplificado
**Estado**: ✅ COMPLETADO  
**Archivos Modificados**:
- `templates/base.html` - Quitar email, mantener solo nombre

**Descripción**:
- Antes: "Nombre Completo" + "email@domain.com"
- Ahora: "Conectado como: Diego" (compacto)
- Mejora experiencia en móvil (menos espacio usado)

**Impacto en BD**: ❌ Ninguno (solo presentación)

---

### CAMBIO 3: Sistema de Venta (SI/NO) en Productos
**Estado**: ✅ COMPLETADO  
**Archivos Modificados**:
- `app/models.py` - Nueva columna `se_vende` (Boolean, default=True)
- `templates/main/crear_producto.html` - Campo select
- `templates/main/editar_producto.html` - Campo select
- `templates/main/productos.html` - Nueva columna en tabla
- `app/main.py` - Lógica para guardar se_vende

**Descripción**:
- Nuevo campo: ¿Se Vende? (SI/NO)
- SI = Producto para venta (Rebelde, Party Box, etc.)
- NO = Ingrediente para lotes (Alcohol, Refrescos, etc.)

**Impacto en BD**: 
- ⚠️ **REQUIERE MIGRACIÓN** (migrate_db.py)
- Columna nueva: `se_vende BOOLEAN DEFAULT 1`
- Productos existentes = todos "SE VENDEN" por defecto

**Script de Migración**: `python migrate_db.py`

---

### CAMBIO 4: Filtros Inteligentes (Nueva Venta / Lotes)
**Estado**: ✅ COMPLETADO  
**Archivos Modificados**:
- `app/main.py` - Función `nueva_venta()` y `nuevo_lote()`

**Descripción**:
```python
# Nueva Venta (línea ~465)
productos = Producto.query.filter_by(activo=True, se_vende=True).all()

# Nuevo Lote (línea ~727)
productos = Producto.query.filter_by(activo=True, se_vende=False).all()
```

**Impacto en BD**: ❌ Ninguno (solo filtros en SELECT)

---

### CAMBIO 5: Zona Horaria Perú (UTC-5)
**Estado**: ✅ COMPLETADO  
**Archivos Modificados**:
- `config.py` - Agregar `TIMEZONE = pytz.timezone('America/Lima')`
- `app/utils.py` - Función `get_current_time()`
- `requirements.txt` - Agregar `pytz` si no está

**Descripción**:
- Las nuevas ventas se registran con hora de Perú (UTC-5)
- Sin desfase de 6-8 horas que tenía antes (hora de España)
- Ventas antiguas mantienen su timestamp (para auditoría)

**Impacto en BD**: ⚠️ FUNCIONAL
- Las nuevas ventas tendrán timestamps correctos
- Las antiguas mantienen su hora original
- No hay cambio de estructura en BD

---

### CAMBIO 6: Scripts de Migración y Backup
**Estado**: ✅ COMPLETADO  
**Archivos Nuevos**:
- `migrate_db.py` - Script de migración de BD
- `backup_restore.py` - Script de export/import JSON
- `ACTUALIZACION_MOVIL_Y_FILTROS.md` - Documentación

**Descripción**:
- `migrate_db.py`: Agrega columna `se_vende` sin perder datos
- `backup_restore.py`: Exporta/importa datos en JSON

**Impacto en BD**: ✅ SEGURO
- No destruye datos existentes
- Crea backups automáticos
- Script idempotente (se puede ejecutar varias veces)

---

### CAMBIO 7: Sistema de Usuarios con Roles/Permisos ⭐ NUEVO
**Estado**: 🔄 EN DESARROLLO  
**Archivos a Modificar**:
- `app/models.py` - Agregar campos `has_permisos` a Usuario
- `app/main.py` - Nueva ruta `/admin/usuarios`
- `templates/main/admin_usuarios.html` - Nueva página (CREAR)
- `templates/base.html` - Agregar opción en sidebar

**Descripción**:
- Campo: `has_permisos` (Boolean) - SI/NO para permisos
- Por ahora: Todos con True (todos pueden hacer todo)
- Futuro: Controlar acceso por permisos

**Estructura de Permisos (Futuro)**:
```
has_permisos = True:
  ✅ Ver todo
  ✅ Crear productos
  ✅ Vender
  ✅ Hacer lotes
  ✅ Ver reportes
  ✅ Editar usuarios

has_permisos = False:
  ❌ Solo ver (read-only)
  ❌ No puede crear/editar
  ❌ No puede vender
  ❌ (Será definido después)
```

**Impacto en BD**: ⚠️ REQUIERE MIGRACIÓN (nueva columna)

---

## ⏱️ PLAZOS Y TIMELINE

### 📅 FASE 1: Implementado (15 de Marzo 2026)
| Cambio | Estado | Fecha | Prioridad |
|--------|--------|-------|-----------|
| Sidebar Responsive | ✅ | 15/03 | 🔴 Alta |
| Panel Usuario Simplificado | ✅ | 15/03 | 🟡 Media |
| Sistema SE_VENDE | ✅ | 15/03 | 🔴 Alta |
| Filtros Inteligentes | ✅ | 15/03 | 🔴 Alta |
| Zona Horaria | ✅ | 15/03 | 🟡 Media |
| Scripts Migración | ✅ | 15/03 | 🟢 Baja |

### 📅 FASE 2: En Desarrollo (Hoy)
| Cambio | Estado | Fecha Est. | Prioridad |
|--------|--------|-----------|-----------|
| Sistema Usuarios/Roles | 🔄 | 15/03 - Hoy | 🔴 Alta |
| Panel de Gestión Usuarios | 🔄 | 15/03 | 🔴 Alta |

### 📅 FASE 3: A Futuro
| Cambio | Estado | Fecha Est. | Prioridad |
|--------|--------|-----------|-----------|
| Restricciones por Permiso | ⏳ | Próximas semanas | 🟡 Media |
| Auditoría de Cambios | ⏳ | Próximas semanas | 🟡 Media |
| Reportes Avanzados | ⏳ | Próximas semanas | 🟢 Baja |
| Integración de Pagos | ⏳ | Futuro | 🟢 Baja |

---

## 🗄️ PLAN DE BASE DE DATOS

### 🔍 ESTADO ACTUAL DE BD

**Ubicación**: `instance/inventario.db` (local) / PythonAnywhere (online)

**Tabla de Usuarios - ANTES**:
```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY,
    nombre_completo VARCHAR(120),
    email VARCHAR(120) UNIQUE,
    password_hash VARCHAR(255),
    activo BOOLEAN DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Tabla de Usuarios - DESPUÉS (v2.1)**:
```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY,
    nombre_completo VARCHAR(120),
    email VARCHAR(120) UNIQUE,
    password_hash VARCHAR(255),
    has_permisos BOOLEAN DEFAULT 1,  -- ⭐ NUEVO
    activo BOOLEAN DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 🚀 CAMBIOS EN BD REQUERIDOS

| Tabla | Acción | Columna | Tipo | Default | Fecha |
|-------|--------|---------|------|---------|-------|
| productos | ADD | se_vende | BOOLEAN | 1 | 15/03 |
| usuarios | ADD | has_permisos | BOOLEAN | 1 | 15/03 |

### 📊 MÉTRICAS ESPERADAS

**Base de Datos - Tamaño**:
- Antes: ~50-100 KB (según ventas)
- Después: +5 KB (nuevas columnas)
- **Total esperado**: ~55-105 KB

**Tiempo de Migración**:
- Columna `se_vende`: < 1 segundo
- Columna `has_permisos`: < 1 segundo
- **Total**: ~ 2 segundos

---

## 🔧 INSTRUCCIONES DE DESPLIEGUE

### PASO 1: Backup Preventivo ⚠️
```bash
# Local (en PowerShell)
python backup_restore.py export

# PythonAnywhere (SSH)
cd /home/azaerodiego/InventarioApp
python backup_restore.py export
```

**Resultado**: Archivo JSON en carpeta `backups/`

---

### PASO 2: Ejecutar Migraciones

**Para Cambio: se_vende**
```bash
python migrate_db.py
```
- Espera mensaje: "✅ Columna 'se_vende' agregada exitosamente"

**Para Cambio: has_permisos**
```bash
python migrate_permisos.py  # (A CREAR)
```

---

### PASO 3: Recargar Aplicación (PythonAnywhere)
1. Web Console → Bash
2. `cd /home/azaerodiego/InventarioApp`
3. `touch /var/www/azaerodiego_pythonanywhere_com_wsgi.py`
   O en Dashboard: Web → Reload ← BOTÓN RELOAD

---

### PASO 4: Verificar Cambios
1. Abre https://azaerodiego.pythonanywhere.com/dashboard
2. Pruebas:
   - ✅ Sidebar responde a pantalla pequeña
   - ✅ Nuevo campo "¿Se Vende?" en productos
   - ✅ Horas correctas en nuevas ventas
   - ✅ Lista filtrada en Nueva Venta
   - ✅ Panel de usuarios en Admin

---

## ↩️ ROLLBACK - En Caso de Error

### Opción 1: Restaurar desde Backup
```bash
python backup_restore.py import backups/backup_YYYYMMDD_HHMMSS.json
```

### Opción 2: Deshacer Cambios Manualmente

**Para quitar `se_vende`**:
```sql
-- NO EJECUTAR EN PRODUCCIÓN SIN BACKUP
ALTER TABLE productos DROP COLUMN se_vende;
-- Volver a versión anterior del código
```

**Para quitar `has_permisos`**:
```sql
-- NO EJECUTAR EN PRODUCCIÓN SIN BACKUP
ALTER TABLE usuarios DROP COLUMN has_permisos;
```

### Opción 3: Volver a Versión Anterior
```bash
# Si tienes git
git revert HEAD~1  # Vuelve al commit anterior

# Si no, descarga el backup JSON
python backup_restore.py import backups/backup_YYYYMMDD_HHMMSS.json
```

---

## 📝 CHECKLIST DE DESPLIEGUE

```
PRE-DESPLIEGUE:
[ ] ✅ Backup creado (backup_restore.py export)
[ ] ✅ Código probado localmente
[ ] ✅ Todos los scripts listos

DESPLIEGUE:
[ ] ✅ Ejecutar migrate_db.py
[ ] ✅ Ejecutar migrate_permisos.py (cuando esté listo)
[ ] ✅ Recargar app en PythonAnywhere
[ ] ✅ Verificar sidebar en móvil
[ ] ✅ Crear nueva venta - verificar horas
[ ] ✅ Acceder a panel de usuarios

POST-DESPLIEGUE:
[ ] ✅ Verificar que las ventas antiguas no se perdieron
[ ] ✅ Revisar BD (tamaño, estructura)
[ ] ✅ Probar en navegador móvil (Chrome/Safari)
[ ] ✅ Documentar resultado en YAML/JSON
```

---

## 🔐 SEGURIDAD Y CONSIDERACIONES

### Contraseñas
- ✅ Ya encriptadas con `werkzeug.security`
- ✅ No se pueden recuperar (only reset)

### Permisos Futuros
- ⚠️ Por ahora todos tienen `has_permisos=True`
- 🔜 Implementar verificaciones en rutas (@require_permisos)

### Auditoría
- ⚠️ NO hay logs de auditoría aún
- 🔜 Agregar tabla `audit_log` (próxima versión)

### Data Privacy
- ✅ Emails únicos por usuario
- ✅ Contraseñas encriptadas
- ❌ NO hay GDPR compliance aún (futuro)

---

## 📞 PREGUNTAS FRECUENTES

**P: ¿Perderemos datos al migrar?**  
R: No. Los scripts de migración son **aditivos** (ADD COLUMN, no DROP)

**P: ¿Funciona con datos antiguos?**  
R: Sí. Productos existentes quedarán con `se_vende=1` (se venden)

**P: ¿Qué pasa si no ejecuto migrate_db.py?**  
R: La app fallará con error "column 'se_vende' not found"

**P: ¿Puedo rollback después?**  
R: Sí, pero debes usar el backup JSON o deshacer cambios en código

**P: ¿La hora se cambió para ventas antiguas?**  
R: No. Solo las NUEVAS ventas usan la zona horaria correcta

**P: ¿Cómo limitar permisos después?**  
R: Actualizando la columna `has_permisos=0` y agregando checks en rutas

---

## 📊 RESUMEN DE CAMBIOS

| Aspecto | Antes | Después | Riesgo |
|--------|-------|---------|--------|
| Sidebar Móvil | No | Sí (Hamburguesa) | ✅ Bajo |
| Panel Usuario | Nombre + Email | "Conectado como" | ✅ Bajo |
| Productos Venta | Todos se venden | SI/NO filtrable | ⚠️ Medio |
| Lista Nueva Venta | Todos productos | Solo venta=SI | ✅ Bajo |
| Lista Lotes | Todos productos | Solo venta=NO | ✅ Bajo |
| Zona Horaria | UTC+2 (España) | UTC-5 (Perú) | ✅ Bajo |
| Sistema Permisos | Nada | SI/NO (todos SI) | ⚠️ Medio |

---

**Versión Next**: 2.2 - Panel de Reportes Mejorado  
**Próxima Revisión**: 22 de Marzo de 2026

---

*Este documento será actualizado conforme se implementen nuevas cambios.*  
*Última actualización: 15 de Marzo de 2026*
