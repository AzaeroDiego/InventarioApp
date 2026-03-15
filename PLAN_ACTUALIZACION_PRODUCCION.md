# 🔄 PLAN DE ACTUALIZACIÓN - MANTENER TODO FUNCIONANDO

**Basado en**: `PYTHONANYWHERE_DESPLIEGUE_PASO_A_PASO.md`  
**Objetivo**: Reemplazar archivos + ejecutar migraciones sin romper nada  
**Tiempo**: 10-15 minutos

---

## 🎯 ANÁLISIS DE LO ACTUAL

### Estructura en PythonAnywhere (Actual)
```
/home/AzaeroDiego/InventarioApp/InventarioApp/
├── app/
│   ├── models.py          ✓ Actual
│   ├── main.py            ✓ Actual
│   ├── auth.py            ✓ Ya existe
│   ├── utils.py           ✓ Ya existe
│   └── __init__.py        ✓ Ya existe
├── templates/
│   ├── base.html          ✓ Actual
│   └── main/
│       └── (otros archivos)
├── run.py                 ✓ Ya existe
├── config.py              ✓ Ya existe
└── instance/
    └── inventario.db      ✓ Base de datos (NO TOCAR)
```

### Configuración en PythonAnywhere (Actual)
- **Dominio**: `azaerodiego.pythonanywhere.com`
- **Python**: 3.12
- **WSGI**: Importa `app` desde `run.py`
- **Virtualenv**: SIN (usa entorno base)
- **Estado**: ✅ FUNCIONANDO

---

## 🚀 PLAN DE ACTUALIZACIÓN (6 PASOS)

### PASO 1: HACER BACKUP (LOCAL)
```bash
# En tu laptop
cd C:\Users\azaer\Documents\Diego\Bering\InventarioApp
python backup_restore.py export
```
✅ **Resultado**: Crea carpeta `backups/` con JSON de datos

---

### PASO 2: PREPARAR ZIP CON CAMBIOS
```bash
# En tu laptop - Excluir estos cuando hagas ZIP:
✗ venv/
✗ __pycache__/
✗ .git/
✗ instance/inventario.db  ← IMPORTANTE: NO INCLUIR BD
✗ backups/                 ← No necesario en servidor

# Incluir TODOS los demás archivos
✓ app/
✓ templates/
✓ static/
✓ run.py
✓ config.py
✓ requirements.txt
✓ migrate_db.py          ← NUEVO
✓ migrate_permisos.py    ← NUEVO
✓ deploy_all.py          ← NUEVO
✓ backup_restore.py      ← NUEVO
```

---

### PASO 3: SUBIR ZIP A PYTHONANYWHERE

#### OPCIÓN A: Por Git (si tienes)
```bash
# Local
git add .
git commit -m "v2.1.1: Panel usuarios, se_vende, permisos"
git push origin main

# PythonAnywhere Bash Console
cd /home/AzaeroDiego/InventarioApp/InventarioApp
git pull origin main
```

#### OPCIÓN B: Por SFTP Manual
```
1. Descargar WinSCP
2. Conectar a azaerodiego.pythonanywhere.com:2222
3. Navegar a: /home/AzaeroDiego/InventarioApp/InventarioApp/
4. Subir archivos (reemplazar)
```

#### OPCIÓN C: Por Bash ZIP (sin Git)
```bash
# Local: Crear InventarioApp_v2.zip

# PythonAnywhere Bash:
cd /home/AzaeroDiego/InventarioApp
rm -rf InventarioApp_old
mv InventarioApp InventarioApp_old
unzip InventarioApp_v2.zip
```

✅ **Resultado**: Archivos actualizados en PythonAnywhere

---

### PASO 4: EJECUTAR MIGRACIONES EN PYTHONANYWHERE

En **Bash Console** de PythonAnywhere:

```bash
cd /home/AzaeroDiego/InventarioApp/InventarioApp

# Migración 1: Agregar se_vende a productos
python migrate_db.py

# Migración 2: Agregar permisos a usuarios
python migrate_permisos.py
```

**Resultado esperado**:
```
✅ Columna 'se_vende' agregada exitosamente.
✅ Columna 'has_permisos' agregada exitosamente.
✅ Columna 'rol' agregada exitosamente.
```

---

### PASO 5: RECARGAR APLICACIÓN

En **PythonAnywhere Dashboard**:

```
1. Ve a pestaña: Web
2. Busca: azaerodiego.pythonanywhere.com
3. Click botón: RELOAD (verde)
4. Espera 30-60 segundos
```

✅ **Resultado**: App reinicia con datos nuevos

---

### PASO 6: VERIFICAR EN NAVEGADOR

```
1. Abre: https://azaerodiego.pythonanywhere.com/dashboard
2. Login: demo@example.com / 123456
3. Navega a: Sidebar → Administración → Gestión de Usuarios
4. Verifica que ves tabla de usuarios con columnas:
   - Nombre Completo
   - Email
   - Rol
   - Permisos (SI/NO)
   - Estado (Activo/Inactivo)
   - Fechas
   - Botones (⚔️ Editar, 🔘 Estado, 🔑 Contraseña)
```

✅ **Resultado**: Panel de usuarios funciona

---

## 📊 ARCHIVOS QUE DEBEN REEMPLAZARSE

```
REEMPLAZAR (Sobrescribir):
[ ] app/models.py                    - Agregar campos has_permisos, rol
[ ] app/main.py                      - Agregar rutas /admin/usuarios
[ ] templates/base.html              - Agregar link en sidebar
[ ] config.py                        - Agregar TIMEZONE (opcional)
[ ] app/utils.py                     - Agregar get_current_time() (opcional)

CREAR NUEVOS:
[ ] templates/main/admin_usuarios.html  - Panel de usuarios
[ ] migrate_db.py                       - Script migración se_vende
[ ] migrate_permisos.py                 - Script migración permisos
[ ] deploy_all.py                       - Script automático (opcional)
[ ] backup_restore.py                   - Script backup (opcional)

NO TOCAR:
[✓] run.py                          - Sin cambios
[✓] instance/inventario.db          - BD está en servidor
[✓] templates/main/* (otros archivos)
[✓] static/                         - Sin cambios
```

---

## 🛡️ SEGURIDAD: CHECKLIST PREVIO

Antes de actualizar, verificar:

```
[ ] ✅ Backup local hecho (python backup_restore.py export)
[ ] ✅ NO incluyo venv/ en el ZIP
[ ] ✅ NO incluyo __pycache__/ en el ZIP
[ ] ✅ NO incluyo instance/inventario.db en el ZIP
[ ] ✅ Todos los archivos .py están bien formados (sin errores de sintaxis)
[ ] ✅ El archivo WSGI en PythonAnywhere sigue igual
```

---

## ⚠️ SI ALGO SALE MAL - ROLLBACK

### Opción 1: Restaurar desde Bash
```bash
cd /home/AzaeroDiego/InventarioApp
mv InventarioApp InventarioApp_broken
mv InventarioApp_old InventarioApp
```

### Opción 2: Restaurar desde Backup JSON
```bash
cd /home/AzaeroDiego/InventarioApp/InventarioApp
python backup_restore.py import /ruta/al/backup.json
```

### Opción 3: Contactar PythonAnywhere support
Si la BD se corrompe.

---

## 📋 ORDEN EXACTO DE COMANDOS (COPIAR-PEGAR)

### EN LOCAL:
```bash
cd C:\Users\azaer\Documents\Diego\Bering\InventarioApp
python backup_restore.py export
# Esperar a que diga "✅ Datos exportados"
```

### EN PYTHONANYWHERE BASH:
```bash
cd /home/AzaeroDiego/InventarioApp/InventarioApp
python migrate_db.py
python migrate_permisos.py
# Esperar a que ambos digan ✅
```

### EN PYTHONANYWHERE DASHBOARD:
```
Web → azaerodiego.pythonanywhere.com → Reload
Esperar 60 segundos
```

### EN NAVEGADOR:
```
Abre: https://azaerodiego.pythonanywhere.com/auth/login
Login: demo@example.com / 123456
Navega: Dashboard → Administración → Gestión de Usuarios
```

---

## 🎯 RESULTADO FINAL ESPERADO

Después de estos 6 pasos, deberías tener:

✅ Base de datos con nuevas columnas  
✅ Panel de usuarios funcionando  
✅ Sistema de permisos instalado  
✅ Filtros SE_VENDE en productos  
✅ Zona horaria correcta en nuevas ventas  
✅ Todos tus datos antiguos preservados  

---

## 🚨 PUNTOS CRÍTICOS

### ❌ NO HAGAS ESTO:
- ❌ NO subas `instance/inventario.db` (ya existe en servidor)
- ❌ NO sobrescribas `run.py, config.py` si no les cambiaste nada
- ❌ NO ejecutes DROP TABLE en la BD
- ❌ NO borres la carpeta `/home/AzaeroDiego/InventarioApp`

### ✅ HAZLO ASÍ:
- ✅ Sube solo los archivos modificados/nuevos
- ✅ Ejecuta migraciones DESPUÉS de subir
- ✅ Recarga la app DESPUÉS de las migraciones
- ✅ Verifica en navegador DESPUÉS de recargar

---

## 📞 PREGUNTAS MÁS FRECUENTES

**P: ¿Cuánto tiempo toma?**  
R: 10-15 minutos. La mayoría es esperar a que suba y se recargue.

**P: ¿Se pierden datos?**  
R: No. Las migraciones son aditivas (ADD COLUMN, no DELETE).

**P: ¿Qué pasa si faltan dependencias?**  
R: PythonAnywhere tiene la mayoría incluidas. Si falta algo, fallaría.

**P: ¿Se puede hacer en móvil?**  
R: No. Necesitas SSH/Bash. Pero el resultado funciona en móvil.

**P: ¿Debo hacer backup?**  
R: SÍ. Siempre. En 1 minuto: `python backup_restore.py export`

---

## 🆘 TROUBLESHOOTING RÁPIDO

| Problema | Causa | Solución |
|----------|-------|----------|
| "Columna no existe" | Migrations no ejecutadas | Ejecuta `python migrate_db.py` |
| "ModuleNotFoundError" | Archivo falta en servidor | Verifica que subiste todos |
| Error 500 en web | WSGI roto o importación falló | Revisa WSGI, revisa `run.py` |
| "Gestión de Usuarios" no aparece | Caché | Limpia caché (Ctrl+Shift+Del) |

---

## ✅ CHECKLIST FINAL

```
PRE-ACTUALIZACIÓN:
[ ] Backup local hecho
[ ] Archivos listos en laptop
[ ] ZIP preparado sin venv/__pycache__

ACTUALIZACIÓN:
[ ] Archivos subidos a PythonAnywhere
[ ] migrate_db.py ejecutado ✓
[ ] migrate_permisos.py ejecutado ✓
[ ] App recargada en Dashboard ✓

POST-ACTUALIZACIÓN:
[ ] https://azaerodiego.pythonanywhere.com/ carga
[ ] Login funciona
[ ] Dashboard visible
[ ] Panel de usuarios visible
[ ] Puedo editar permisos de un usuario

VERIFICACIÓN DE DATOS:
[ ] Ventas antiguas siguen ahí
[ ] Productos antiguos siguen ahí
[ ] Usuarios antiguos siguen ahí
[ ] Nueva venta solo muestra productos con se_vende=1
```

---

**¿Tienes Git configurado o usas ZIP manual?**

Te guío paso a paso desde ahí mismo.

