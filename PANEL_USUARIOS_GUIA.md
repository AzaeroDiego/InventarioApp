# 👥 PANEL DE GESTIÓN DE USUARIOS - GUÍA DE INSTALACIÓN

**Versión**: 2.1.1  
**Fecha**: 15 de Marzo de 2026  
**Estado**: ✅ LISTO PARA DESPLEGAR

---

## 🎯 ¿QUÉ INCLUYE ESTE PANEL?

### Funcionalidades Principales
✅ **Visualizar todos los usuarios** del sistema  
✅ **Ver permisos de cada usuario** (SI/NO)  
✅ **Cambiar permisos** en tiempo real  
✅ **Asignar roles** (Admin, Gerente, Vendedor)  
✅ **Activar/Desactivar usuarios**  
✅ **Resetear contraseñas** (temporal: 123456)  
✅ **Información de permisos** (qué pueden hacer)  

---

## 🚀 PASOS DE INSTALACIÓN

### PASO 1: Actualizar Código
```bash
# Descargar/copiar los archivos nuevos al servidor:
- app/main.py (actualizado con rutas)
- app/models.py (actualizado con campos)
- templates/base.html (actualizado con sidebar)
- templates/main/admin_usuarios.html (NUEVO)
- migrate_permisos.py (NUEVO script)
```

### PASO 2: Ejecutar Migración de Permisos
```bash
# En local:
python migrate_permisos.py

# Resultado esperado:
# ✅ Columna 'has_permisos' agregada exitosamente.
#    Todos los usuarios existentes tienen permisos = SI
# ✅ Columna 'rol' agregada exitosamente.
#    Todos los usuarios existentes tienen rol = 'vendedor'
```

### PASO 3: Recargar Aplicación (PythonAnywhere)
```bash
# En PythonAnywhere Dashboard:
1. Ve a la sección "Web"
2. Haz clic en el botón "Reload" 
3. Espera 30 segundos a que reinicie

# O por SSH:
touch /var/www/azaerodiego_pythonanywhere_com_wsgi.py
```

### PASO 4: Verificar Instalación
1. Abre https://azaerodiego.pythonanywhere.com/dashboard
2. En el sidebar, busca: **Administración → Gestión de Usuarios**
3. Si ves la tabla de usuarios 👤 ¡Está funcionando!

---

## 📋 ESTRUCTURA DE LA BASE DE DATOS

### Tabla `usuarios` - NUEVAS COLUMNAS

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `has_permisos` | BOOLEAN | 1 (True) | Permisos SI/NO |
| `rol` | VARCHAR(50) | 'vendedor' | admin, gerente, vendedor |
| `fecha_actualizacion` | DATETIME | NOW | Cuándo se modificó |

### Ejemplo de BD después de migración:
```sql
id | nombre_completo | email                | has_permisos | rol       | activo | fecha_creacion
1  | Demo Usuario    | demo@example.com     | 1 (SI)       | vendedor  | 1      | 2024-01-01
2  | Diego Admin     | diego@example.com    | 1 (SI)       | admin     | 1      | 2024-01-02
```

---

## 🎮 CÓMO USAR EL PANEL

### 1️⃣ ACCEDER AL PANEL
```
Dashboard → Sidebar → Administración → Gestión de Usuarios
```

### 2️⃣ EDITAR PERMISOS DE UN USUARIO
```
1. Click en botón ⚔️ (Escudo) en la fila del usuario
2. Se abre un modal (ventana emergente)
3. Cambiar:
   - Rol: Admin / Gerente / Vendedor
   - Permisos: ✓ Activar o desactivar
4. Click "Guardar Cambios"
```

### 3️⃣ CAMBIAR ESTADO DE USUARIO
```
1. Click en botón 🔘 (Power) en la fila
2. Confirmar en el alert
3. Usuario se activa/desactiva automáticamente
```

### 4️⃣ RESETEAR CONTRASEÑA
```
1. Click en botón 🔑 (Key) en la fila
2. Confirmar en el alert
3. Contraseña se resetea a: 123456
4. Avisar al usuario que debe cambiarla
```

---

## 🔐 SISTEMA DE PERMISOS (EXPLICADO)

### ✅ PERMISOS = SI (Completos)
El usuario puede hacer **TODO**:
- ✅ Ver dashboard y reportes
- ✅ Crear, editar y eliminar productos
- ✅ Registrar ventas
- ✅ Preparar lotes
- ✅ Ver historial completo
- ✅ Acceder a "Editar Productos"
- ⭐ **Acceder a Panel de Usuarios** (si es admin)

### ❌ PERMISOS = NO (Solo Lectura - FUTURO)
El usuario solo puede **VER** (cuando se implemente):
- ✅ Ver dashboard (read-only)
- ✅ Ver productos (no editar)
- ✅ Ver ventas (no crear)
- ✅ Ver lotes (no crear)
- ❌ NO puede crear, editar, eliminar
- ❌ NO puede preparar lotes
- ❌ NO puede registrar ventas
- ❌ NO puede acceder a Admin

---

## 📊 ROLES DISPONIBLES

| Rol | Descripción | Permisos | Uso |
|-----|-------------|----------|-----|
| 👑 **Admin** | Administrador del sistema | Completos | Tú (Diego) - Control total |
| 💼 **Gerente** | Supervisor/Gerente | Completos | Jefes de equipo |
| 👤 **Vendedor** | Personal de ventas | Completos | Vendedores normales |

**Nota**: Por ahora TODOS tienen permisos, sin importar el rol.  
La restricción se implementará en próximas versiones.

---

## 📱 COMPATIBILIDAD MÓVIL

El panel funciona en móviles:
- ✅ Tabla responsive
- ✅ Botones adaptados
- ✅ Modales funcionales
- ✅ Diseño mobile-first

---

## 🔧 TROUBLESHOOTING

### Error: "Ruta no encontrada" al acceder al panel
```
Solución: Asegúrate de haber ejecutado migrate_permisos.py
```

### Error: "Columna 'has_permisos' no existe"
```
Solución: Ejecuta nuevamente:
python migrate_permisos.py
```

### El botón "Gestión de Usuarios" no aparece en el sidebar
```
Solución: 
1. Limpia caché del navegador (Ctrl+Shift+Delete)
2. Recarga la página (Ctrl+F5)
3. Si persiste, recarga la app en PythonAnywhere
```

### "No tienes permisos para acceder a esta sección"
```
Solución: Solo usuarios con has_permisos=1 pueden acceder
El usuario demo@example.com debe tener has_permisos=SI
```

---

## 📝 EJEMPLOS DE USO

### Escenario 1: Agregar nuevo vendedor con contraseña temporal
```
1. El vendedor se registra desde la página de registro
2. Las contraseña tiene 6+ caracteres validados
3. Ir a Panel → Gestión de Usuarios
4. Buscar al nuevo vendedor
5. Sus permisos están en SI por defecto
6. Listo para trabajar
```

### Escenario 2: Desactivar usuario (permiso temporal)
```
1. Ir a Panel → Gestión de Usuarios
2. Encontrar al usuario
3. Click botón 🔘 (Power)
4. Estado cambia a "Inactivo"
5. No puede hacer login hasta reactivarlo
```

### Escenario 3: Usuario olvida contraseña
```
1. Ir a Panel → Gestión de Usuarios
2. Click botón 🔑 (Key)
3. Contraseña se resetea a: 123456
4. Avisar al usuario
5. El usuario hace login con 123456
6. En próxima versión: obligar cambio de contraseña
```

---

## 🔄 PRÓXIMOS PASOS (FUTURO)

### Próxima Versión (v2.2):
- [ ] Implementar restricciones según `has_permisos=0`
- [ ] Agregar auditoría (quién cambió qué)
- [ ] Gráficos de actividad de usuarios
- [ ] Exportar reporte de usuarios

### Versión v2.3:
- [ ] Dos factores de autenticación (2FA)
- [ ] Recuperación de contraseña por email
- [ ] Logs de login/logout
- [ ] Sesiones por dispositivo

---

## ✅ CHECKLIST FINAL

```
ANTES DE DESPLEGAR:
[ ] Has descargado todos los archivos nuevos
[ ] Has hecho backup (python backup_restore.py export)
[ ] Has probado localmente
[ ] El comando migrate_permisos.py funciona

EN PYTHONANYWHERE:
[ ] Subiste los archivos
[ ] Ejecutaste migrate_permisos.py en SSH
[ ] Recargaste la aplicación (Reload)
[ ] Esperas 1-2 minutos

VERIFICACIÓN:
[ ] Login funcionando
[ ] Dashboard accesible
[ ] Panel de usuarios visible en sidebar
[ ] Tabla de usuarios muestra todos los usuarios
[ ] Botones funcionan (escudo, power, key)
[ ] Modal abre y cierra correctamente
```

---

## 📞 PREGUNTAS FRECUENTES

**P: ¿Se pierden datos al migrar?**  
R: No. Los scripts son aditivos (ADD, no DROP). Todos tus usuarios se mantienen.

**P: ¿Qué pasa si no ejecuto migrate_permisos.py?**  
R: La app fallará con error "column 'has_permisos' not found".

**P: ¿Puedo cambiar permisos en tiempo real?**  
R: Sí, los cambios son inmediatos en BD. El usuario verá cambios en próximo login.

**P: ¿Los usuarios con permisos=NO ven diferencias?**  
R: Ahora no. Se aplicarán restricciones en próximas versiones.

**P: ¿Cómo hago que solo admin vea este panel?**  
R: Ya está implementado. Solo usuarios con `has_permisos=True` pueden acceder.

**P: ¿Qué ocurre si reseteo contraseña?**  
R: Se cambia a 123456. El usuario debe cambiarla en próximo login (futuro).

---

**Versión**: 2.1.1  
**Última actualización**: 15 de Marzo de 2026  
**Estado**: ✅ Listo para Producción

Para más información, ver: `CAMBIOS_Y_PLAZOS.md`
