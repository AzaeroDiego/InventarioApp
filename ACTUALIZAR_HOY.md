# 🎯 RESUMEN EJECUTIVO - ACTUALIZAR PRODUCCIÓN HOY

**Basado en tu setup actual**  
**Tiempo**: 15 minutos  
**Riesgo**: BAJO (tienes backup)

---

## 📌 TU SETUP ACTUAL en PythonAnywhere

```
Servidor: /home/AzaeroDiego/InventarioApp/InventarioApp/
BD: inventario.db (En servidor, NO modificar)
Python: 3.12
WSGI: Importa app desde run.py
Status: ✅ FUNCIONA
```

---

## 🚀 LO QUE DEBES HACER (3 PASOS SIMPLES)

### PASO 1️⃣: HACER BACKUP (5 minutos)
```bash
cd C:\Users\azaer\Documents\Diego\Bering\InventarioApp
python backup_restore.py export
```
✅ Crea archivo JSON con todos tus datos

---

### PASO 2️⃣: SUBIR ARCHIVOS NUEVOS (5 minutos)

#### SI TIENES GIT:
```bash
git add .
git commit -m "v2.1.1: Panel usuarios"
git push origin main
```

#### SI NO TIENES GIT:
```
1. Descargar WinSCP
2. Conectar a: azaerodiego.pythonanywhere.com:2222
3. Usuario: azaerodiego
4. Contraseña: (tu pwd de PythonAnywhere)
5. Navegar a: /home/AzaeroDiego/InventarioApp/InventarioApp/
6. Drag & drop estos archivos:
   - app/models.py (reemplazar)
   - app/main.py (reemplazar)
   - templates/base.html (reemplazar)
   - templates/main/admin_usuarios.html (nuevo)
   - migrate_db.py (nuevo)
   - migrate_permisos.py (nuevo)
```

---

### PASO 3️⃣: EJECUTAR MIGRACIONES (5 minutos)

En **PythonAnywhere Bash Console**:

```bash
cd /home/AzaeroDiego/InventarioApp/InventarioApp
python migrate_db.py
python migrate_permisos.py
```

Espera a ver:
```
✅ Columna 'se_vende' agregada
✅ Columna 'has_permisos' agregada
✅ Columna 'rol' agregada
```

---

### PASO 4️⃣: RECARGAR (1 minuto)

En **PythonAnywhere Dashboard**:
```
Web → Click Reload (botón verde)
```

Espera 30 segundos.

---

### PASO 5️⃣: VERIFICAR (2 minutos)

Abre en navegador:
```
https://azaerodiego.pythonanywhere.com/dashboard
Login: demo@example.com / 123456
Sidebar → Administración → Gestión de Usuarios
```

Si ves tabla de usuarios ✅ ¡ÉXITO!

---

## 🎁 RESULTADO FINAL

Tendrás:
- ✅ Panel de Usuarios funcionando
- ✅ Sistema de Permisos (SI/NO)
- ✅ Columna "Se Vende" en Productos
- ✅ Todos tus datos preservados
- ✅ Zona Horaria correcta

---

## ❓ DECISIÓN CRÍTICA

**¿Tienes Git configurado o usas ZIP/SFTP?**

Responde y te guío EXACTO paso a paso para tu caso.

A) Git  
B) SFTP/WinSCP  
C) No sé

