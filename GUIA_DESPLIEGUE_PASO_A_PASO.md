# 📋 GUÍA PASO A PASO - DESPLIEGUE EN PYTHONANYWHERE

**Fecha**: 15 de Marzo de 2026  
**Versión**: 2.1.1 (Con Usuarios y Permisos)  
**Tiempo estimado**: 10-15 minutos

---

## 🎯 OPCIONES DE DESPLIEGUE

### OPCIÓN A: DESPLIEGUE AUTOMÁTICO (RECOMENDADO ⭐)
```bash
python deploy_all.py production
```
**Ventajas**: 
- ✅ Un comando lo hace todo
- ✅ Validaciones automáticas
- ✅ Resumen final
- ✅ Rollback fácil si hay error

**Tiempo**: ~3-5 minutos

---

### OPCIÓN B: DESPLIEGUE MANUAL PASO A PASO
Para mayor control. Sigue esta guía.

---

## 🚀 OPCIÓN A: DESPLIEGUE AUTOMÁTICO

### PASO 1: Descargar Script
El archivo `deploy_all.py` ya está en tu proyecto.

### PASO 2: Ejecutar en Local (Prueba)
```bash
cd C:\Users\azaer\Documents\Diego\Bering\InventarioApp
python deploy_all.py development
```

**Resultado esperado**:
```
✅ [HH:MM:SS] PASO 1: CREAR BACKUP
✅ [HH:MM:SS] Backup de datos completado
✅ [HH:MM:SS] PASO 2: MIGRAR COLUMNA 'SE_VENDE'
✅ [HH:MM:SS] Migración de productos completado
...
🎉 ¡DESPLIEGUE EXITOSO!
```

### PASO 3: Ejecutar en PythonAnywhere
```
1. SSH a PythonAnywhere:
   - Terminal → "Open bash console" en PythonAnywhere

2. Navegar:
   cd /home/azaerodiego/InventarioApp

3. Ejecutar script:
   python deploy_all.py production

4. Confirmar cuando pida (responde: si)

5. Espera a que termine

6. Si dice "ACCIÓN MANUAL":
   En PythonAnywhere Dashboard → Web → Click Reload (botón verde)
```

### PASO 4: Verificar
```
1. Abre: https://azaerodiego.pythonanywhere.com/dashboard
2. Sidebar → Administración → Gestión de Usuarios
3. Si ves la tabla de usuarios: ¡ÉXITO! ✅
```

---

## 🛠️ OPCIÓN B: DESPLIEGUE MANUAL PASO A PASO

### PASO 1A: HACER BACKUP (LOCAL)
```bash
cd C:\Users\azaer\Documents\Diego\Bering\InventarioApp
python backup_restore.py export
```

**Qué hace**:
- Exporta todos tus datos a `backups/backup_YYYYMMDD_HHMMSS.json`
- Puedes restaurar si algo sale mal

**Verificar**: Debería crear una carpeta `backups/` con archivo JSON

---

### PASO 2A: MIGRAR SE_VENDE (LOCAL)
```bash
python migrate_db.py
```

**Qué hace**:
- Agrega columna `se_vende` a tabla `productos`
- Todos quedan con `se_vende=1` (SE VENDEN)

**Resultado esperado**:
```
✅ Columna 'se_vende' agregada exitosamente.
   Todos los productos existentes están marcados como 'SE VENDE = SI'
```

---

### PASO 3A: MIGRAR PERMISOS (LOCAL)
```bash
python migrate_permisos.py
```

**Qué hace**:
- Agrega columna `has_permisos` a tabla `usuarios`
- Agrega columna `rol` a tabla `usuarios`
- Todos quedan con `has_permisos=1` (PERMISOS SI)

**Resultado esperado**:
```
✅ Columna 'has_permisos' agregada exitosamente.
   Todos los usuarios existentes tienen permisos = SI
✅ Columna 'rol' agregada exitosamente.
   Todos los usuarios existentes tienen rol = 'vendedor'
```

---

### PASO 4A: SUBIR CAMBIOS A PYTHONANYWHERE

#### Opción B1: Por Git (si lo tienes configurado)
```bash
git add .
git commit -m "v2.1.1: Panel de usuarios, permisos y se_vende"
git push origin main
```

#### Opción B2: Por SFTP/Bash Manual
```
1. SSH a PythonAnywhere:
   cd /home/azaerodiego/InventarioApp

2. Descargar archivos:
   # Si tienes git
   git pull origin main
   
   # O copiar manualmente los archivos nuevos

3. Ejecutar migraciones en PythonAnywhere:
   python migrate_db.py
   python migrate_permisos.py
```

---

### PASO 5A: RECARGAR APP EN PYTHONANYWHERE
```
Dashboard PythonAnywhere:
1. Click en "Web"
2. Busca tu app: azaerodiego.pythonanywhere.com
3. Click botón verde "Reload"
4. Espera 30-60 segundos
5. Listo! ✅
```

---

### PASO 6A: VERIFICAR EN PRODUCCIÓN
```
1. Abre: https://azaerodiego.pythonanywhere.com/dashboard
2. Login con: demo@example.com / 123456
3. Sidebar → Administración → Gestión de Usuarios
4. Debería mostrarte tabla con todos los usuarios
5. Prueba editar permisos (botón ⚔️)
```

---

## 📊 COMPARACIÓN: AUTO vs MANUAL

| Aspecto | Automático | Manual |
|--------|-----------|--------|
| **Tiempo** | 3-5 min | 10-15 min |
| **Complejidad** | 1 comando | 6 pasos |
| **Errores** | Detecta auto | Tienes que notar |
| **Control** | Menos | Más |
| **Para principiantes** | ✅ SÍ | ❌ NO |
| **Para expertos** | ✅ RÁPIDO | ✅ CONTROL |

**RECOMENDACIÓN**: Usa automático la primera vez, manual si necesitas debugging.

---

## ✅ CHECKLIST DE DESPLIEGUE

```
PRE-DESPLIEGUE:
[ ] Hice backup (python backup_restore.py export)
[ ] Subí todos los archivos nuevos
[ ] Actualicé app/models.py
[ ] Actualicé app/main.py  
[ ] Actualicé templates/base.html
[ ] Copié templates/main/admin_usuarios.html
[ ] Copié migrate_permisos.py
[ ] Copié deploy_all.py

DURANTE DESPLIEGUE:
[ ] Ejecuté python deploy_all.py production (o pasos manuales)
[ ] Recibí confirmación de éxito
[ ] Recargué la app en PythonAnywhere

POST-DESPLIEGUE:
[ ] Accedí a dashboard
[ ] Vi sidebar con "Gestión de Usuarios"
[ ] Abrí página de usuarios
[ ] Vi tabla con usuarios
[ ] Probé editar permisos (modal abrió)
[ ] Probé resetear contraseña
[ ] Probé activar/desactivar usuario
[ ] Registré nueva venta (verificar "Se Vende" filtro)
```

---

## 🐛 TROUBLESHOOTING

### Problema: "Comando deploy_all.py no encontrado"
```
Solución: 
cd C:\Users\azaer\Documents\Diego\Bering\InventarioApp
python deploy_all.py production
(asegúrate de estar en la carpeta correcta)
```

### Problema: "Columna no existe" al desplegar
```
Solución:
1. Verifica que execute migrate_db.py
2. Verifica que execute migrate_permisos.py
3. Recarga la aplicación en PythonAnywhere
```

### Problema: "Gestión de Usuarios" no aparece en sidebar
```
Solución:
1. Limpia caché (Ctrl+Shift+Delete)
2. Recarga página (Ctrl+F5)
3. Verifica que templates/base.html tenga el link
4. Recarga app en PythonAnywhere
```

### Problema: Modal no abre al hacer clic
```
Solución:
1. Abre consola del navegador (F12)
2. Verifica que no haya errores JavaScript
3. Recarga la página
4. Prueba en otro navegador
```

### Problema: "No tienes permisos para acceder"
```
Solución:
En PythonAnywhere bash:
   python -c "
   from app import create_app, db
   from app.models import Usuario
   app = create_app('production')
   with app.app_context():
       todos = Usuario.query.all()
       for u in todos:
           u.has_permisos = True
           print(f'{u.email}: has_permisos=True')
       db.session.commit()
   "
```

---

## 📱 PRUEBAS POST-DESPLIEGUE

### Test 1: Dashboard
```
✓ Login funciona
✓ Dashboard carga sin errores
✓ Sidebar visible (móvil y desktop)
```

### Test 2: Panel de Usuarios
```
✓ Sidebar → Administración → Gestión de Usuarios
✓ Tabla muestra todos los usuarios
✓ Botones ⚔️ (permisos), 🔘 (estado), 🔑 (contraseña) visibles
```

### Test 3: Editar Permisos
```
✓ Click ⚔️ → Abre modal
✓ Modal muestra rol y checkbox has_permisos
✓ Cambiar y guardar → Mensaje de éxito
```

### Test 4: Cambiar Estado
```
✓ Click 🔘 → Pide confirmación
✓ Usuario cambia de "Activo" a "Inactivo"
✓ Click 🔘 de nuevo → Vuelve a "Activo"
```

### Test 5: Resetear Contraseña
```
✓ Click 🔑 → Pide confirmación
✓ Mensaje: "Contraseña reseteada a 123456"
✓ Avisar usuario de nueva contraseña
```

### Test 6: Nueva Venta - Filtro SE_VENDE
```
✓ Nueva Venta → Lista desplegable
✓ Solo muestra productos con se_vende=1
✓ No muestra ingredientes (se_vende=0)
```

### Test 7: Nuevo Lote - Filtro INGREDIENTES
```
✓ Nuevo Lote → Seleccionar ingredientes
✓ Solo muestra productos con se_vende=0
✓ No muestra productos de venta (se_vende=1)
```

---

## 🎉 ¡ÉXITO!

Si llegaste aquí y todo funciona:

✅ Tienes panel de usuarios  
✅ Tienes sistema de permisos (SI/NO)  
✅ Tienes columna SE_VENDE en productos  
✅ Tienes filtros inteligentes en ventas/lotes  
✅ Tienes zona horaria correcta  
✅ Tienes backup de datos  

**Versión actual**: 2.1.1  
**Próxima versión**: 2.2 (Restricciones de permisos)

---

## 📞 PREGUNTAS FINALES

**P: ¿Qué hago si los cambios no aparecen?**  
R: Recarga la app en PythonAnywhere y limpia caché del navegador (Ctrl+Shift+Del)

**P: ¿Puedo deshacer los cambios?**  
R: Sí, tengo el backup. Restaura con: `python backup_restore.py import backups/backup_XXX.json`

**P: ¿Los datos se pierden?**  
R: No. Las migraciones son ADITIVAS. Solo agregan columnas, no eliminan.

**P: ¿Puedo hacer esto en móvil?**  
R: No. Necesitas SSH/Terminal. Pero el resultado funciona perfecto en móvil.

---

**Última actualización**: 15 de Marzo de 2026  
**Autor**: Sistema Automático  
**Estado**: ✅ Listo para Producción
