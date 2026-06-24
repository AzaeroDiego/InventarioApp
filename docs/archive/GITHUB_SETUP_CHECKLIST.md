# ✅ GitHub + PythonAnywhere — Checklist Interactivo

**Tiempo estimado**: 15 minutos  
**Dificultad**: Fácil (copiar-pegar)

---

## 🔧 FASE 1: CREAR REPO EN GITHUB (3 min)

### ☐ Paso 1: Crear repositorio
1. Ir a: https://github.com/new
2. Nombre: `InventarioApp`
3. Descripción: `Sistema de Gestión de Inventario`
4. Privado o Público: Tu elección
5. **NO inicializar con README**
6. Click **Create repository**

**Resultado esperado**: URL como `https://github.com/AzaeroDiego/InventarioApp.git`

Guarda esa URL → **LA NECESITARÁS EN PASO 4**

---

## 💻 FASE 2: GIT LOCAL EN TU PC (5 min)

### ☐ Paso 2: Crear .gitignore

En PowerShell (Windows), desde tu carpeta del proyecto:

```bash
cd C:\Users\azaer\Documents\Diego\Bering\InventarioApp

# Crear archivo .gitignore
ni .gitignore
```

**Contenido para pegar en .gitignore**:

```
# Python
__pycache__/
*.pyc
venv/
env/
.Python
*.egg-info/
dist/
build/

# Flask
instance/
.webassets-cache

# Database (IMPORTANTE: no subir BD)
instance/inventario.db
*.db

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Temp
*.tmp
*~
```

Guardar archivo.

---

### ☐ Paso 3: Inicializar Git local

```bash
# En PowerShell, desde tu carpeta del proyecto
git init

git config user.name "Diego"
git config user.email "diego@example.com"

git add .

git status
# Verificar que NO veas:
#   - instance/inventario.db
#   - __pycache__
#   - venv

git commit -m "v2.1.1: Panel usuarios, permisos, se_vende, timezone"
```

---

### ☐ Paso 4: Conectar con GitHub y subir

```bash
# Reemplaza con la URL que guardaste en Paso 1
git remote add origin https://github.com/AzaeroDiego/InventarioApp.git

git branch -M main

git push -u origin main
```

**Esperado**: Te pide usuario/contraseña de GitHub (o genera un token)

✅ **Tu código está en GitHub**

---

## 🔑 FASE 3: CONFIGURAR SSH EN PYTHONANYWHERE (5 min)

### ☐ Paso 5: Generar clave SSH

En PythonAnywhere → **Consoles** → Abre **Bash Console**:

```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
```

(Solo presiona Enter, no escribe preguntas)

Luego:

```bash
cat ~/.ssh/id_rsa.pub
```

**Copia TODA la salida** (comienza con `ssh-rsa` y termina con `...@pythonanywhere`)

---

### ☐ Paso 6: Agregar clave SSH a GitHub

1. Ir a: https://github.com/settings/keys
2. Click **New SSH key**
3. Title: `PythonAnywhere`
4. Key: Pega todo lo que copiaste
5. Click **Add SSH key**

---

### ☐ Paso 7: Probar conexión SSH

En PythonAnywhere Bash Console:

```bash
ssh -T git@github.com
```

**Esperado**:
```
Hi AzaeroDiego! You've successfully authenticated, but GitHub does not provide shell access.
```

✅ **SSH está funcionando**

---

## 📦 FASE 4: CLONAR EN PYTHONANYWHERE (2 min)

### ☐ Paso 8: Limpiar estructura vieja (OPCIONAL)

```bash
cd /home/AzaeroDiego/InventarioApp

# Si tienes el proyecto viejo:
mv InventarioApp InventarioApp_backup_zip
mkdir InventarioApp
cd InventarioApp
```

---

### ☐ Paso 9: Clonar desde GitHub

```bash
# Asegúrate de estar en /home/AzaeroDiego/InventarioApp
cd /home/AzaeroDiego/InventarioApp

# Clonar con el punto al final (importante)
git clone git@github.com:AzaeroDiego/InventarioApp.git .
```

**Esperado**: Ve descargar archivos

```
Cloning into '.'...
...
Checking out files... done.
```

---

## 🗄️ FASE 5: EJECUTAR MIGRACIONES

### ☐ Paso 10: Correr scripts de migración

```bash
cd /home/AzaeroDiego/InventarioApp/InventarioApp

python migrate_db.py
python migrate_permisos.py
```

**Esperado**:
```
✅ Columna 'se_vende' agregada
✅ Columna 'has_permisos' agregada
✅ Columna 'rol' agregada
```

---

## 🔄 FASE 6: RECARGAR EN PYTHONANYWHERE

### ☐ Paso 11: Recargar aplicación

1. Dashboard de PythonAnywhere
2. Tab **Web**
3. Click botón **Reload** (verde)
4. Esperar 30-60 segundos

---

## ✨ FASE 7: VERIFICAR

### ☐ Paso 12: Probar en browser

1. Abre: https://azaerodiego.pythonanywhere.com
2. Login: `demo@example.com` / `123456`
3. Sidebar → **Administración** → **Gestión de Usuarios**
4. Deberías ver tabla con: Nombre, Email, Rol, Permisos, Estado, etc.

✅ **¡ÉXITO!**

---

## 🎯 PRÓXIMAS VECES (Rápido)

### Para actualizar código:

**En tu PC**:
```bash
cd C:\Users\azaer\Documents\Diego\Bering\InventarioApp

# Editar archivos...

git add .
git commit -m "Descripción del cambio"
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

**En Dashboard**:
```
Reload
```

⏱️ **Total: 2 minutos**

---

## 🆘 Si algo falla

| Problema | Solución |
|----------|----------|
| "Permission denied (publickey)" | Verifica que copiaste TODA la clave SSH. Vuelve al Paso 6 |
| "Repository not found" | Verifica que el repo es público. Vuelve al Paso 1 |
| "destination path ... already exists" | Usa: `git clone git@github.com:..." .` (con punto) |
| "fatal: destination path" | Borra carpeta y reintentar Paso 9 |

---

## 📖 Referencia completa

Para más detalles, ver: `GITHUB_PYTHONANYWHERE_FLUJO.md`

---

✅ **¡Checklist completado!**

Tu proyecto está ahora versionado en GitHub y conectado con PythonAnywhere.
