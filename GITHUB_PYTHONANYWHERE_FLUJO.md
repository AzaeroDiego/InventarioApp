# 📘 FLUJO GITHUB + PYTHONANYWHERE (RECOMENDADO)

**Versión**: 2.1.1  
**Fecha**: 15 de Marzo de 2026  
**Método**: Git + GitHub + SSH

---

## 🎯 VENTAJAS vs ZIP Manual

| Aspecto | ZIP Manual | GitHub |
|--------|-----------|--------|
| **Actualización** | Volver a subir ZIP | `git pull` |
| **Versionado** | No | Sí (`git log`) |
| **Rollback** | Restaurar backup | `git revert` |
| **Colaboración** | No hay | Fácil |
| **Auditoría** | No | Sí (quién cambió qué) |
| **Automatización** | No | Posible (webhooks) |

---

## 🚀 PLAN PASO A PASO

### FASE 1: PREPARAR LOCAL CON GIT

#### PASO 1A: Crear repositorio en GitHub

1. Ir a: https://github.com/new
2. Crear repositorio:
   - **Name**: `InventarioApp`
   - **Description**: Sistema de Gestión de Inventario
   - **Public/Private**: Tu elección (recomendado Private)
   - **NO inicializar con README**
3. Click "Create repository"
4. Copiar URL del repositorio (HTTPS o SSH)

**Ejemplo HTTPS**: `https://github.com/AzaeroDiego/InventarioApp.git`

---

#### PASO 1B: Inicializar Git en Local

En PowerShell, desde tu carpeta del proyecto:

```bash
cd C:\Users\azaer\Documents\Diego\Bering\InventarioApp

# Inicializar git
git init

# Crear archivo .gitignore (IMPORTANTE)
ni .gitignore
```

**Contenido de `.gitignore`** (copiar-pegar):
```
# Virtual Environment
venv/
env/
ENV/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Flask
instance/
.webassets-cache

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Database (NO SUBIR, es local)
instance/inventario.db
*.db

# Backups
backups/

# Archivos temporales
*.tmp
*~

# Private keys
.ssh/
*.pem
```

Guardar archivo.

---

#### PASO 1C: Agregar cambios a Git

```bash
# Ver status
git status

# Agregar todos los archivos (excepto los del .gitignore)
git add .

# Verificar qué se va a subir
git status
```

**Esperado**: Deberías ver archivos verdes, pero NO:
- `instance/inventario.db`
- `__pycache__/`
- `venv/`

---

#### PASO 1D: Primer commit

```bash
git config user.name "Diego"
git config user.email "diego@example.com"

git commit -m "v2.1.1: Panel usuarios, permisos, se_vende, zona horaria"
```

---

#### PASO 1E: Conectar con GitHub (HTTPS)

```bash
# Reemplaza con tu URL de GitHub
git remote add origin https://github.com/AzaeroDiego/InventarioApp.git

# Cambiar rama a main (si aún es master)
git branch -M main

# Subir a GitHub
git push -u origin main
```

✅ **Resultado**: Tu código está en GitHub

---

### FASE 2: CONFIGURAR PYTHONANYWHERE CON SSH

#### PASO 2A: Generar clave SSH en PythonAnywhere

En **Bash Console** de PythonAnywhere:

```bash
# Generar clave SSH
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""

# Ver la clave pública
cat ~/.ssh/id_rsa.pub
```

**Copiar TODA la salida** (comienza con `ssh-rsa` y termina con username@host)

---

#### PASO 2B: Agregar clave SSH a GitHub

1. Ir a: https://github.com/settings/keys
2. Click "New SSH key"
3. Title: `PythonAnywhere`
4. Key: Pegar todo lo que copiaste
5. Click "Add SSH key"

---

#### PASO 2C: Probar conexión SSH

En **Bash Console** de PythonAnywhere:

```bash
ssh -T git@github.com
```

**Esperado**:
```
Hi AzaeroDiego! You've successfully authenticated, but GitHub does not provide shell access.
```

✅ Conexión OK

---

### FASE 3: CLONAR REPOSITORIO EN PYTHONANYWHERE

#### PASO 3A: Limpiar estructura antigua (OPCIONALMENTE)

Si ya tienes el proyecto en ZIP:

```bash
cd /home/AzaeroDiego/InventarioApp

# Hacer backup del proyecto viejo
mv InventarioApp InventarioApp_backup_zip

# Crear carpeta nueva para clonar
mkdir InventarioApp
cd InventarioApp
```

---

#### PASO 3B: Clonar repositorio

```bash
# Usar SSH (más seguro que HTTPS)
git clone git@github.com:AzaeroDiego/InventarioApp.git .
```

**Nota**: El `.` al final clona DENTRO de la carpeta actual.

**Resultado**:
```
/home/AzaeroDiego/InventarioApp/InventarioApp/
├── app/
├── templates/
├── static/
├── run.py
├── config.py
├── migrate_db.py
├── migrate_permisos.py
└── .git/
```

---

#### PASO 3C: Ejecutar migraciones

```bash
# Asegúrate de estar en la carpeta correcta
cd /home/AzaeroDiego/InventarioApp/InventarioApp

# Ejecutar migraciones
python migrate_db.py
python migrate_permisos.py
```

✅ **Resultado**:
```
✅ Columna 'se_vende' agregada
✅ Columna 'has_permisos' agregada
✅ Columna 'rol' agregada
```

---

### FASE 4: CONFIGURAR PYTHONANYWHERE

#### PASO 4A: Actualizar Source Code en Web App

En **PythonAnywhere Dashboard** → **Web**:

```
Source code: /home/AzaeroDiego/InventarioApp/InventarioApp
Working directory: /home/AzaeroDiego/InventarioApp/InventarioApp
```

(Debería quedar igual, solo para verificar)

---

#### PASO 4B: Verificar WSGI sigue igual

El WSGI debe importar desde `run.py`:

```python
import sys
import os

project_home = '/home/AzaeroDiego/InventarioApp/InventarioApp'
if project_home not in sys.path:
    sys.path.append(project_home)

from run import app as application
```

---

#### PASO 4C: Recargar

Click botón **Reload** (verde)

---

### FASE 5: VERIFICAR

```
1. Abre: https://azaerodiego.pythonanywhere.com/dashboard
2. Login: demo@example.com / 123456
3. Sidebar → Administración → Gestión de Usuarios
4. Verifica que ves tabla de usuarios
```

✅ **¡ÉXITO!**

---

## 🔄 FUTURAS ACTUALIZACIONES (Lo Fácil)

Ahora que tienes GitHub + PythonAnywhere sincronizados:

### Para actualizar:

**En local**:
```bash
# Hacer cambios
# Editar archivos...

# Commit
git add .
git commit -m "Descripción del cambio"

# Subir
git push origin main
```

**En PythonAnywhere Bash**:
```bash
cd /home/AzaeroDiego/InventarioApp/InventarioApp
git pull origin main
# Si hay cambios en BD:
python migrate_db.py
python migrate_permisos.py
```

**En PythonAnywhere Dashboard**:
```
Click Reload
```

**¡Listo en 1 minuto!** vs 15 minutos con ZIP.

---

## 🆘 TROUBLESHOOTING GITHUB + PYTHONANYWHERE

### Error: "Permission denied (publickey)"
```
Solución:
1. Verifica que copiaste TODA la clave SSH
2. Verifica que está en Settings → SSH Keys de GitHub
3. Prueba de nuevo: ssh -T git@github.com
```

### Error: "Repository not found"
```
Solución:
1. Verifica URL correcta
2. Verifica que el repo es público O tienes acceso
3. Verifica SSH key está agregada a GitHub
```

### Error: "fatal: destination path '' already exists"
```
Solución:
git clone git@github.com:AzaeroDiego/InventarioApp.git .
(Usa . al final, no InventarioApp)
```

### ¿Cómo volver atrás si hay problema?
```bash
# Ver historial
git log --oneline

# Volver a commit anterior
git revert <hash>
git push origin main
```

---

## 📊 ESTRUCTURA FINAL

```
GitHub:
  AzaeroDiego/InventarioApp
  ├── main branch
  ├── Historial de commits
  └── SSH access

PythonAnywhere:
  /home/AzaeroDiego/InventarioApp/InventarioApp/
  ├── Clonado de GitHub
  ├── .git/ (para hacer git pull)
  ├── BD en instance/inventario.db
  └── WSGI apuntando a run.py
```

---

## ✅ CHECKLIST FINAL

```
GITHUB:
[ ] Repositorio creado en GitHub
[ ] .gitignore en local
[ ] git init hecho
[ ] Primer commit hecho
[ ] Código subido a main branch

PYTHONANYWHERE:
[ ] Clave SSH generada
[ ] Clave SSH agregada a GitHub
[ ] Conexión SSH probada (ssh -T git@github.com)
[ ] Repositorio clonado
[ ] Migraciones ejecutadas
[ ] WSGI verificado
[ ] App recargada

VERIFICACIÓN:
[ ] https://azaerodiego.pythonanywhere.com/ abre
[ ] Login funciona
[ ] Panel de usuarios visible
[ ] git status en PythonAnywhere muestra "On branch main"
```

---

## 💡 RECOMENDACIONES

1. **Haz commits frecuentes** - No esperes a tener 20 cambios
2. **Escribe mensajes claros** - "Agregar panel usuarios" vs "cambios"
3. **Usa ramas** - Para features grandes: `git checkout -b feature/nueva-caracteristica`
4. **Revisa antes de push** - `git diff` antes de `git add`
5. **Mantén `.gitignore`** - NO subas datos sensibles

---

**Ahora que tienes GitHub + PythonAnywhere, cada actualización es 10 veces más fácil.**

¿Quieres que siga adelante con GitHub o tienes dudas?
