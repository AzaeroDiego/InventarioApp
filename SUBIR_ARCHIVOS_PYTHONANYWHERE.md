# 📤 GUÍA: SUBIR ARCHIVOS A PYTHONANYWHERE + EJECUTAR

**Versión**: 2.1.1  
**Fecha**: 15 de Marzo de 2026  
**Estado**: ✅ LISTO

---

## 🎯 RESUMEN DEL PROCESO

```
1. ✅ Archivos en tu laptop
2. ⬆️ SUBIR a PythonAnywhere ← AQUÍ ESTAMOS
3. ⚙️ Ejecutar migraciones en PythonAnywhere
4. 🔄 Recargar aplicación
5. ✨ Verificar en navegador
```

---

## 📊 ARCHIVOS QUE NECESITAS SUBIR

| Archivo | Tipo | Acción | Prioridad |
|---------|------|--------|-----------|
| `app/models.py` | Modificado | Reemplazar | 🔴 CRÍTICO |
| `app/main.py` | Modificado | Reemplazar | 🔴 CRÍTICO |
| `templates/base.html` | Modificado | Reemplazar | 🔴 CRÍTICO |
| `templates/main/admin_usuarios.html` | ✨ NUEVO | Crear | 🔴 CRÍTICO |
| `migrate_db.py` | ✨ NUEVO | Crear | 🟡 IMPORTANTE |
| `migrate_permisos.py` | ✨ NUEVO | Crear | 🟡 IMPORTANTE |
| `deploy_all.py` | ✨ NUEVO | Crear | 🟢 OPCIONAL |
| `backup_restore.py` | ✨ NUEVO | Crear | 🟢 OPCIONAL |

**Total**: 8 archivos (4 nuevos, 4 modificados)

---

## 🚀 OPCIÓN 1: SUBIR POR GIT (RECOMENDADO)

### SI TIENES GIT CONFIGURADO:

```bash
# En tu laptop - PASO 1: Commit cambios
cd C:\Users\azaer\Documents\Diego\Bering\InventarioApp
git add .
git commit -m "v2.1.1: Panel usuarios, permisos, se_vende"
git push origin main
```

### En PythonAnywhere - PASO 2: Descargar cambios

```bash
# Abrir Bash Console en PythonAnywhere
ssh -i /home/azaerodiego/.ssh/id_rsa azaerodiego@ssh.pythonanywhere.com

# Luego:
cd /home/azaerodiego/InventarioApp
git pull origin main

# Verificar que los archivos están:
ls -la app/models.py
ls -la templates/main/admin_usuarios.html
ls -la migrate_permisos.py
```

### PASO 3: Ejecutar migraciones

```bash
python migrate_db.py
python migrate_permisos.py
```

### PASO 4: Recargar app
```bash
# En PythonAnywhere Dashboard → Web → Click Reload
```

---

## 💻 OPCIÓN 2: SUBIR POR SFTP (MANUAL)

### SI NO TIENES GIT:

#### Paso 1: Descargar FileZilla o WinSCP
- **FileZilla**: https://filezilla-project.org/
- **WinSCP**: https://winscp.net/

#### Paso 2: Conectar a PythonAnywhere
```
Host: sftp://azaerodiego.pythonanywhere.com
Username: azaerodiego
Password: (tu contraseña de PythonAnywhere)
Port: 2222
```

#### Paso 3: Navegar a carpeta
```
Remoto: /home/azaerodiego/InventarioApp/
Local: C:\Users\azaer\Documents\Diego\Bering\InventarioApp
```

#### Paso 4: Subir archivos
```
MODIFICADOS (Reemplazar):
✓ app/models.py
✓ app/main.py
✓ templates/base.html

NUEVOS (Crear):
✓ templates/main/admin_usuarios.html
✓ migrate_db.py
✓ migrate_permisos.py
✓ deploy_all.py
✓ backup_restore.py
```

#### Paso 5: Ejecutar migraciones
En PythonAnywhere Bash:
```bash
cd /home/azaerodiego/InventarioApp
python migrate_db.py
python migrate_permisos.py
```

---

## ⚡ OPCIÓN 3: COPIAR-PEGAR POR BASH (MÁS RÁPIDO)

### SI TIENES SSH ACCESO:

Esta es la forma más rápida para archivos pequeños.

#### Paso 1: Abrir Bash en PythonAnywhere

```bash
cd /home/azaerodiego/InventarioApp
```

#### Paso 2: Editar archivos directamente

**PARA CADA ARCHIVO, HACER:**

##### A. `app/models.py` - REEMPLAZAR SECCIÓN

```bash
# Editar con nano
nano app/models.py

# Encontrar la clase Usuario (línea ~6)
# Buscar: has_permisos, rol, fecha_actualizacion
# Si NO existen, agregar:
```

```python
class Usuario(UserMixin, db.Model):
    """Modelo de usuario para autenticación"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    has_permisos = db.Column(db.Boolean, default=True)  # ← NUEVO
    rol = db.Column(db.String(50), default='vendedor')  # ← NUEVO
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # ← NUEVO
```

```bash
# Guardar: Ctrl+O, Enter, Ctrl+X
```

##### B. `app/main.py` - AGREGAR IMPORT Y RUTAS

```bash
nano app/main.py

# Al inicio, cambiar:
# De: from app.models import Producto, Categoria, ...
# A: from app.models import Producto, Categoria, ..., Usuario
```

Luego al final del archivo (antes del cierre), agregar:

```python
# ============ ADMINISTRACIÓN DE USUARIOS ============

@main_bp.route('/admin/usuarios')
@login_required
def admin_usuarios():
    """Administración de usuarios y permisos"""
    if not current_user.has_permisos:
        flash('No tienes permisos para acceder a esta sección.', 'error')
        return redirect(url_for('main.dashboard'))
    
    usuarios = Usuario.query.order_by(Usuario.fecha_creacion.desc()).all()
    return render_template('main/admin_usuarios.html', usuarios=usuarios)


@main_bp.route('/admin/usuario/<int:id>/editar-permisos', methods=['POST'])
@login_required
def editar_permisos_usuario(id):
    """Editar permisos de un usuario"""
    if not current_user.has_permisos:
        flash('No tienes permisos para esta acción.', 'error')
        return redirect(url_for('main.dashboard'))
    
    usuario = Usuario.query.get_or_404(id)
    has_permisos = request.form.get('has_permisos', '0') == '1'
    usuario.has_permisos = has_permisos
    
    rol = request.form.get('rol', usuario.rol)
    if rol in ['admin', 'vendedor', 'gerente']:
        usuario.rol = rol
    
    db.session.commit()
    status = "activados" if has_permisos else "desactivados"
    flash(f'Permisos de {usuario.nombre_completo} {status}.', 'success')
    return redirect(url_for('main.admin_usuarios'))


@main_bp.route('/admin/usuario/<int:id>/cambiar-estado', methods=['POST'])
@login_required
def cambiar_estado_usuario(id):
    """Activar/desactivar usuario"""
    if not current_user.has_permisos:
        flash('No tienes permisos para esta acción.', 'error')
        return redirect(url_for('main.dashboard'))
    
    usuario = Usuario.query.get_or_404(id)
    usuario.activo = not usuario.activo
    db.session.commit()
    
    status = "activado" if usuario.activo else "desactivado"
    flash(f'Usuario {usuario.nombre_completo} {status}.', 'success')
    return redirect(url_for('main.admin_usuarios'))


@main_bp.route('/admin/usuario/<int:id>/resetear-contraseña', methods=['POST'])
@login_required
def resetear_contrasena(id):
    """Resetear contraseña de usuario"""
    if not current_user.has_permisos:
        flash('No tienes permisos para esta acción.', 'error')
        return redirect(url_for('main.dashboard'))
    
    usuario = Usuario.query.get_or_404(id)
    temp_password = '123456'
    usuario.set_password(temp_password)
    db.session.commit()
    
    flash(f'Contraseña de {usuario.nombre_completo} reseteada a: {temp_password}', 'warning')
    return redirect(url_for('main.admin_usuarios'))


@main_bp.route('/api/usuarios/lista')
@login_required
def api_usuarios_lista():
    """API para obtener lista de usuarios"""
    usuarios = Usuario.query.filter_by(activo=True).all()
    return jsonify([{
        'id': u.id,
        'nombre_completo': u.nombre_completo,
        'email': u.email,
        'rol': u.rol,
        'has_permisos': u.has_permisos
    } for u in usuarios])
```

```bash
# Guardar: Ctrl+O, Enter, Ctrl+X
```

---

## 📋 CHECKLIST RÁPIDO - OPCIÓN MÁS FÁCIL

### SI TIENES GIT (RECOMENDADO):

```bash
# Laptop
git add .
git commit -m "v2.1.1"
git push origin main

# PythonAnywhere Bash
cd /home/azaerodiego/InventarioApp
git pull origin main
python migrate_db.py
python migrate_permisos.py

# Dashboard
Click Reload (botón verde)
```

### SI NO TIENES GIT:

```bash
# Descargar WinSCP/FileZilla
# Conectar por SFTP
# Subir 8 archivos
# PythonAnywhere Bash:
python migrate_db.py
python migrate_permisos.py

# Dashboard
Click Reload
```

---

## ✅ VERIFICACIÓN POST-SUBIDA

En PythonAnywhere Bash:

```bash
# Verificar que archivos existen
ls -la app/models.py
ls -la templates/main/admin_usuarios.html
ls -la migrate_permisos.py

# Debe mostrar los archivos con timestamp reciente
```

---

## 🚨 ERRORES COMUNES

### Error: "No such file or directory"
```
Solución: Asegúrate que subiste los archivos a la carpeta correcta:
/home/azaerodiego/InventarioApp/
```

### Error: "Permission denied"
```
Solución: En bash, ejecuta:
chmod +x *.py
```

### Error: "git pull falló"
```
Solución: Si no tienes git, usa SFTP o copia manual por Bash
```

---

## 📊 TIMELINE ESTIMADO

| Paso | Tiempo | Método |
|------|--------|--------|
| Subir archivos | 2-3 min | Git o SFTP |
| Ejecutar migraciones | 1-2 min | Bash |
| Recargar app | 1-2 min | Dashboard |
| Verificar en navegador | 1 min | Navegador |
| **TOTAL** | **5-8 minutos** | - |

---

## 🎯 RESUMEN COMPLETO

### PASO 1: SUBIR ARCHIVOS
```
Opción A (Git): git push
Opción B (SFTP): Drag & drop
Opción C (Bash): nano + copiar-pegar
```

### PASO 2: EJECUTAR MIGRACIONES
```bash
python migrate_db.py
python migrate_permisos.py
```

### PASO 3: RECARGAR APP
```
PythonAnywhere Dashboard → Web → Click Reload
```

### PASO 4: VERIFICAR
```
https://azaerodiego.pythonanywhere.com/dashboard
Sidebar → Administración → Gestión de Usuarios
```

---

## 🚀 ¿CUÁL OPCIÓN ELIJO?

**RECOMENDACIÓN**:

✅ **Si tienes Git**: Opción 1 (Git Push)
- Rápido y seguro
- Todo versionado
- Fácil de revertir

✅ **Si no tienes Git**: Opción 2 (SFTP/WinSCP)
- Interfaz gráfica
- Menos confuso
- Drag & drop

❌ **No recomiendo Bash manual**: 
- Tedioso
- Más propenso a errores
- Lento

---

**¿Cuál tienes configurado? ¿Git o SFTP?**

Te guío paso a paso desde ahí. 🚀
