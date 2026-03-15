# Despliegue de InventarioApp en PythonAnywhere — guía paso a paso

> **⭐ NUEVO MARZO 2026**: Se recomienda usar **GitHub + SSH** en lugar de ZIP manual.  
> Ve a: **`GITHUB_SETUP_CHECKLIST.md`** (copiar-pegar, 15 min) o **`GITHUB_PYTHONANYWHERE_FLUJO.md`** (completo).  
> Para índice de documentación: Ver **`GITHUB_INDICE_DOCUMENTACION.md`**

---

## Objetivo

Este documento explica **exactamente qué se hizo** para que la web de `InventarioApp` quedara funcionando en PythonAnywhere, escrito para otra IA o persona **sin ningún contexto previo**.

La idea es que sirva como **bitácora + manual de repetición**.

---

## Contexto inicial

- Cuenta de PythonAnywhere: `AzaeroDiego`
- Proyecto local en Windows:
  `C:\Users\azaer\Documents\Diego\Bering\InventarioApp`
- Se subió manualmente un archivo comprimido:
  `InventarioApp.zip`
- El proyecto es una aplicación web en **Flask**
- El sitio público quedó en:
  `https://azaerodiego.pythonanywhere.com`
- El login quedó accesible en:
  `https://azaerodiego.pythonanywhere.com/auth/login`

---

## ⭐ ALTERNATIVA RECOMENDADA — GitHub + SSH (NUEVO)

**A partir de Marzo 2026**, se recomienda usar **GitHub + SSH** en lugar de ZIP manual.

### Ventajas
- ✅ Actualizaciones futuras en **1 minuto** (`git pull`)
- ✅ Historial completo de cambios (`git log`)
- ✅ Fácil rollback si algo falla
- ✅ Versionado profesional
- ✅ No necesita re-crear ZIP cada vez

### Flujo recomendado
1. Crear repositorio en GitHub
2. Hacer `git init` local y subir código
3. Generar clave SSH en PythonAnywhere
4. Agregar clave SSH a GitHub
5. Clonar repositorio en PythonAnywhere con `git clone`
6. Ejecutar migraciones
7. Recargar desde PythonAnywhere

### Documentación completa
**→ Ver archivo**: `GITHUB_PYTHONANYWHERE_FLUJO.md`

**Recomendación**: Sigue ese documento si eres nuevo en Git.

---

## Resumen corto del método antiguo (ZIP manual)

Este documento original explica el proceso usado antes (por ZIP manual).

Si prefieres la alternativa GitHub + SSH, ve al documento referenciado arriba.

Si aún quieres usar ZIP, sigue estos pasos:

1. Se ingresó a la cuenta de PythonAnywhere.
2. Se creó una carpeta del proyecto en el servidor.
3. Se subió `InventarioApp.zip`.
4. Se descomprimió el archivo dentro del servidor.
5. Se creó una **Web App manual** en PythonAnywhere.
6. Se apuntó esa Web App al código del proyecto.
7. Se intentó usar un virtualenv propio.
8. Aparecieron problemas de espacio / compatibilidad de entorno.
9. Se dejó el sitio funcionando **sin virtualenv**, usando el entorno base del servidor.
10. Se configuró el archivo **WSGI** para cargar `run.py`.
11. Se recargó la Web App.
12. Se verificó que la página cargara correctamente.

---

# ==========================================

# 🚀 SECCIÓN NUEVA (Marzo 2026) — GitHub + SSH

# ==========================================

## Por qué cambiar de ZIP a GitHub

El método ZIP manual funciona, pero es **repetitivo y propenso a errores**:

| Tarea | ZIP Manual | GitHub |
|-------|-----------|--------|
| Cada actualización | Crear ZIP nuevo → Subir → Descomprimir (10 min) | `git push` local + `git pull` en servidor (1 min) |
| Revisar cambios | Comparar archivos manualmente | `git log` ve todo |
| Problemas | Restaurar ZIP viejo | `git revert` |
| Colaboración | No posible | Fácil |

---

## Plan rápido: GitHub + SSH

### PASO 1: LOCAL (Git Init)
```bash
cd C:\Users\azaer\Documents\Diego\Bering\InventarioApp

# Inicializar git
git init
git config user.name "Diego"
git config user.email "diego@example.com"

# Crear .gitignore (NO subir: venv/, __pycache__/, instance/inventario.db)
# Ver GITHUB_PYTHONANYWHERE_FLUJO.md para contenido completo

# Subir a GitHub
git add .
git commit -m "v2.1.1: Panel usuarios, permisos, se_vende, timezone"
git remote add origin https://github.com/AzaeroDiego/InventarioApp.git
git branch -M main
git push -u origin main
```

### PASO 2: PYTHONANYWHERE (SSH Setup)
En **Bash Console** de PythonAnywhere:
```bash
# Generar clave SSH
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""

# Ver la clave
cat ~/.ssh/id_rsa.pub
# Copiar todo y agregarlo a: https://github.com/settings/keys

# Probar conexión
ssh -T git@github.com
# Resultado esperado: "Hi AzaeroDiego! You've successfully authenticated..."
```

### PASO 3: PYTHONANYWHERE (Clone)
```bash
cd /home/AzaeroDiego/InventarioApp

# Opcional: backup de proyecto anterior
mv InventarioApp InventarioApp_backup_zip

# Clonar repositorio
mkdir InventarioApp
cd InventarioApp
git clone git@github.com:AzaeroDiego/InventarioApp.git .

# Ejecutar migraciones
python migrate_db.py
python migrate_permisos.py
```

### PASO 4: PYTHONANYWHERE (Recargar)
- Dashboard → **Web** → Click **Reload**
- Esperar 30-60 segundos
- Probar en https://azaerodiego.pythonanywhere.com

---

## Futuras actualizaciones (now it's easy!)

### Para cambiar código:
```bash
# En tu PC
git add .
git commit -m "Descripción"
git push origin main
```

### Para actualizar servidor:
```bash
# En PythonAnywhere Bash
cd /home/AzaeroDiego/InventarioApp/InventarioApp
git pull origin main
# Si hay cambios en BD:
python migrate_db.py
python migrate_permisos.py
```

### Para recargar:
Dashboard → **Web** → **Reload**

**¡Listo!** Todo en menos de 2 minutos.

---

## Documentación completa

Guía paso a paso completa (con troubleshooting):  
→ Ver: `GITHUB_PYTHONANYWHERE_FLUJO.md`

---

# ==========================================

# MÉTODO ANTIGUO (ZIP MANUAL) — Referencia

# ==========================================

**Nota**: Este es el método usado inicialmente. Se recomienda GitHub + SSH (arriba).

Si aún prefieres ZIP, sigue los pasos que están debajo.

---

## Paso 1. Entrar al panel de PythonAnywhere

Se inició sesión en:

- `https://www.pythonanywhere.com/user/AzaeroDiego/`

---

## Paso 2. Ir a la sección Files

Desde el panel se entró a **Files** para trabajar con archivos del servidor.

Objetivo:
- crear una carpeta donde viviría el proyecto
- subir el zip del proyecto

---

## Paso 3. Crear carpeta para el proyecto

Se creó una carpeta en el home del usuario, algo equivalente a:

```bash
/home/AzaeroDiego/InventarioApp
```

---

## Paso 4. Subir el archivo ZIP

Dentro de esa carpeta se subió manualmente:

```bash
InventarioApp.zip
```

Este archivo venía desde la PC local.

---

# PARTE 2 — Descompresión del proyecto

## Paso 5. Abrir una consola Bash

Desde la pestaña **Consoles** se abrió una consola Bash nueva.

---

## Paso 6. Ir a la carpeta del proyecto

En consola se trabajó dentro de:

```bash
cd ~/InventarioApp
```

---

## Paso 7. Descomprimir el zip

Se descomprimió el archivo con:

```bash
unzip InventarioApp.zip
```

### Resultado esperado
Después de eso debía existir una estructura parecida a esta:

```bash
/home/AzaeroDiego/InventarioApp/InventarioApp
```

Es decir:

- una carpeta contenedora: `InventarioApp`
- y dentro, la carpeta real del proyecto también llamada `InventarioApp`

> Nota: esta duplicidad de nombre vino de cómo estaba armado el zip.

---

# PARTE 3 — Creación de la Web App

## Paso 8. Ir a la pestaña Web

Desde PythonAnywhere se abrió la sección:

- **Web**

---

## Paso 9. Crear una nueva Web App

Se pulsó:

- **Add a new web app**

Y se eligió:

- dominio por defecto de PythonAnywhere
- configuración **Manual**
- versión de Python: **3.12**

> Importante: se eligió **Manual Configuration**, no plantilla automática.

---

# PARTE 4 — Configuración de rutas de la Web App

## Paso 10. Configurar Source code y Working directory

En la pantalla de configuración de la Web App se llenaron las rutas del proyecto apuntando a la carpeta real del código.

Se usó esta ruta:

```bash
/home/AzaeroDiego/InventarioApp/InventarioApp
```

Esto se colocó como referencia de código / directorio de trabajo de la aplicación.

---

# PARTE 5 — Intento de virtualenv y problema encontrado

## Paso 11. Intentar usar un entorno virtual

Se intentó crear / usar un virtualenv para que la app corriera en un entorno controlado.

La idea era algo como:

```bash
mkvirtualenv --python=/usr/bin/python3.12 inventario-env
```

o variantes similares.

---

## Paso 12. Problema real encontrado

Durante el proceso aparecieron dos problemas:

### Problema A — compatibilidad de versión
En algún momento había una referencia a un entorno anterior que no coincidía bien con Python 3.12.

### Problema B — espacio / cuota
El intento de instalar dependencias o mantener un virtualenv propio generó fricción por la cuota de disco / espacio disponible del plan gratis.

Eso hacía que el despliegue se volviera innecesariamente frágil.

---

## Decisión tomada

**Se eliminó la referencia al virtualenv** y se dejó la Web App sin virtualenv asignado.

Eso hizo que PythonAnywhere use el entorno base del sistema para ejecutar la app.

### Consecuencia
- la web pudo arrancar
- pero si en el futuro faltan paquetes no incluidos por defecto, habrá que:
  - crear un virtualenv más limpio, o
  - reducir dependencias, o
  - usar un plan con más recursos

---

# PARTE 6 — Configuración del archivo WSGI

## Paso 13. Abrir el archivo WSGI de la Web App

PythonAnywhere genera un archivo WSGI para cada sitio.

Se abrió el WSGI correspondiente al dominio de la cuenta.

---

## Paso 14. Cambiar el contenido del WSGI

Se configuró el WSGI para que cargue el proyecto Flask desde `run.py`.

La lógica aplicada fue:

```python
import sys
import os

project_home = '/home/AzaeroDiego/InventarioApp/InventarioApp'
if project_home not in sys.path:
    sys.path.append(project_home)

from run import app as application
```

### Qué significa esto
- agrega la carpeta del proyecto al `sys.path`
- importa el objeto `app` desde `run.py`
- lo expone como `application`, que es lo que espera PythonAnywhere

---

## Supuesto clave para que esto funcione

Dentro del proyecto debe existir algo como esto en `run.py`:

```python
from app import create_app

app = create_app()
```

O alguna variante equivalente en Flask donde `app` sea el objeto principal.

---

# PARTE 7 — Recarga y prueba final

## Paso 15. Recargar la aplicación

Después de ajustar el WSGI y quitar el virtualenv, se pulsó:

- **Reload**

en la pestaña **Web**.

---

## Paso 16. Probar la URL pública

Se abrió:

```text
https://azaerodiego.pythonanywhere.com
```

y también:

```text
https://azaerodiego.pythonanywhere.com/auth/login
```

### Resultado
La página cargó correctamente y mostró el login.

Eso confirmó que:

- el WSGI estaba bien
- la ruta del proyecto estaba bien
- la app Flask estaba arrancando
- el sitio público ya estaba en línea

---

# Estado final en que quedó funcionando

## URL pública

```text
https://azaerodiego.pythonanywhere.com
```

## Login directo

```text
https://azaerodiego.pythonanywhere.com/auth/login
```

## Carpeta del proyecto

```bash
/home/AzaeroDiego/InventarioApp/InventarioApp
```

## WSGI usado

La Web App quedó apuntando a `run.py` mediante WSGI.

## Virtualenv

No quedó uno funcional asignado al final.

La app quedó corriendo con el entorno base del servidor.

---

# Qué cosas NO se hicieron o quedaron a medias

Para dejar claro el contexto real:

1. **No se dejó un flujo Git/GitHub**
   - el despliegue fue por ZIP manual

2. **No se consolidó un virtualenv estable**
   - se intentó, pero por espacio / fricción del plan gratis se optó por dejarlo sin virtualenv

3. **No se documentó automáticamente la lista exacta de dependencias instaladas**
   - porque el entorno final quedó usando el sistema base

4. **No se hizo una migración funcional de nuevas features**
   - solo se dejó la app publicada

---

# Cómo repetir este proceso desde cero

## Flujo mínimo recomendado

### En local
1. editar el proyecto en tu PC
2. probarlo localmente
3. comprimirlo como ZIP

### En PythonAnywhere
4. subir el ZIP a `~/InventarioApp`
5. abrir Bash Console
6. descomprimir:
   ```bash
   cd ~/InventarioApp
   unzip InventarioApp.zip
   ```
7. ir a **Web**
8. crear o actualizar la Web App manual
9. apuntar Source code / Working directory a:
   ```bash
   /home/AzaeroDiego/InventarioApp/InventarioApp
   ```
10. revisar el WSGI y dejar:
   ```python
   import sys
   import os

   project_home = '/home/AzaeroDiego/InventarioApp/InventarioApp'
   if project_home not in sys.path:
       sys.path.append(project_home)

   from run import app as application
   ```
11. dejar vacío el campo de virtualenv si vuelve a dar problemas
12. pulsar **Reload**
13. probar la URL pública

---

# Recomendaciones para futuras actualizaciones

## Recomendación 1
No descomprimas un ZIP nuevo **encima** del proyecto viejo sin revisar.

Mejor:

```bash
mv InventarioApp InventarioApp_backup
unzip InventarioApp.zip
```

y luego pruebas.

---

## Recomendación 2
No subas cosas innecesarias al ZIP:

- `venv`
- `__pycache__`
- `.git`
- logs
- archivos temporales
- bases grandes si no hacen falta

---

## Recomendación 3
Cuando el proyecto crezca, migra a **GitHub + git pull** en lugar de ZIP manual.

---

## Recomendación 4
Si alguna dependencia no existe en el entorno base de PythonAnywhere, habrá que:

- crear un virtualenv limpio
- instalar solo lo estrictamente necesario
- o considerar un plan superior

---

# Diagnóstico rápido si vuelve a fallar

## Si sale error 500
Revisar:
- pestaña **Web**
- **Error log**
- WSGI path
- ruta del proyecto
- imports en `run.py`

## Si no encuentra módulos
Revisar:
- si la app depende de paquetes no instalados
- si hace falta virtualenv

## Si no carga templates o archivos estáticos
Revisar:
- estructura interna del ZIP
- que no haya quedado una carpeta anidada inesperada
- rutas de `templates/` y `static/`

---

# Texto breve para otra IA

Si otra IA tuviera que continuar desde aquí, este sería el resumen ejecutivo:

> El proyecto Flask `InventarioApp` fue desplegado manualmente en PythonAnywhere por ZIP.  
> Se subió `InventarioApp.zip` a `~/InventarioApp`, se descomprimió y la carpeta real del código quedó en `/home/AzaeroDiego/InventarioApp/InventarioApp`.  
> Se creó una Web App manual en Python 3.12.  
> El WSGI quedó configurado para importar `app` desde `run.py` con:
> `from run import app as application`.  
> El virtualenv fue retirado por problemas prácticos de espacio / compatibilidad, así que la app quedó usando el entorno base del servidor.  
> La web funciona públicamente en `https://azaerodiego.pythonanywhere.com` y el login en `https://azaerodiego.pythonanywhere.com/auth/login`.

---

# Fin del documento
---

## 📚 DOCUMENTACIÓN RELACIONADA

Estos archivos complementan este documento:

| Archivo | Uso |
|---------|-----|
| `GITHUB_PYTHONANYWHERE_FLUJO.md` | **→ Guía completa GitHub + SSH** (RECOMENDADO) con todos los detalles, troubleshooting y checklist |
| `PYTHONANYWHERE_DESPLIEGUE_PASO_A_PASO.md` | Este archivo (como referencia ZIP) |
| `PLAN_ACTUALIZACION_PRODUCCION.md` | Estrategia general de deployment con rollback |
| `GUIA_DESPLIEGUE_PASO_A_PASO.md` | Versión manual paso a paso sin automatización |

---

## 🎯 TU SIGUIENTE PASO

### Opción A: GitHub + SSH (RECOMENDADO)
📄 **Sigue**: `GITHUB_PYTHONANYWHERE_FLUJO.md`

Ventajas:
- Fácil de actualizar (próximas veces)
- Historial versionado
- Profesional

---

### Opción B: ZIP Manual (Rápido)
📄 **Sigue**: Las secciones de "MÉTODO ANTIGUO" arriba en este documento

Ventajas:
- Más rápido la primeira vez (10 min)
- No necesita GitHub

Desventajas:
- Cada actualización es lenta (10 min + errores)
- Sin versionado

---