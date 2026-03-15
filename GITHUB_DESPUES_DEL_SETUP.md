# 🎓 Después del Setup: Cómo Mantener tu Proyecto

**Versión**: 2.1.1  
**Para**: Después de completar `GITHUB_SETUP_CHECKLIST.md`

---

## ✅ Confirmación: Ya completaste

Si llegaste aquí es que:

- [x] Repositorio en GitHub creado
- [x] Código subido a GitHub
- [x] SSH configurado en PythonAnywhere
- [x] Repositorio clonado en PythonAnywhere
- [x] Migraciones ejecutadas
- [x] App recargada
- [x] Verificada en: https://azaerodiego.pythonanywhere.com

**¡Felicidades!** 🎉

---

## 🔄 De ahora en adelante: El ciclo fácil

### Escenario 1: Quiero hacer cambios al código

**En tu PC**:

```bash
# Navega a tu carpeta del proyecto
cd C:\Users\azaer\Documents\Diego\Bering\InventarioApp

# Edita los archivos que necesites
# Por ejemplo: edit app/main.py, templates/base.html, etc.

# Ver qué cambió
git status

# Agregar cambios
git add .

# Crear "punto de guardado" (commit)
git commit -m "Descripción breve del cambio"
# Ejemplos:
# "Agregar nuevo reporte de ventas"
# "Corregir bug en filtro de productos"
# "Mejorar UI del panel de usuarios"

# Subir a GitHub
git push origin main
```

**En PythonAnywhere Bash Console**:

```bash
# Ir a la carpeta
cd /home/AzaeroDiego/InventarioApp/InventarioApp

# Descargar cambios desde GitHub
git pull origin main
```

**En PythonAnywhere Dashboard**:

1. Tab **Web**
2. Click **Reload** (botón verde)
3. Esperar 30-60 segundos

**En browser**:
```
https://azaerodiego.pythonanywhere.com → Verifica que funcione
```

✅ **Cambios en vivo**

---

### Escenario 2: Hay cambios en la base de datos

Si agregaste nuevas columnas o tablas, ejecutar:

**En PythonAnywhere Bash**:

```bash
cd /home/AzaeroDiego/InventarioApp/InventarioApp

python migrate_db.py
python migrate_permisos.py

# O tu script de migración personalizado
```

Luego recargar desde Dashboard.

---

### Escenario 3: Algo se rompió, quiero volver atrás

**Opción A: Rápido (último commit)**

```bash
# En tu PC
git revert HEAD --no-edit
git push origin main

# En PythonAnywhere
git pull origin main
# Reload
```

**Opción B: A un punto anterior específico**

```bash
# Ver historial
git log --oneline

# Volver a un commit específico
git revert <hash_del_commit>
git push origin main

# En PythonAnywhere
git pull origin main
# Reload
```

---

## 📊 Ver historial de cambios

```bash
# Últimos 5 cambios
git log --oneline -5

# Ver qué cambió en un archivo específico
git log app/main.py --oneline

# Ver detalle completo de un cambio
git show <hash>

# Ver diferencia entre dos versiones
git diff main origin/main
```

---

## 🌿 Trabajar con ramas (AVANZADO)

Si quieres probar cambios sin afectar `main`:

```bash
# Crear rama nueva
git branch feature/nueva-funcionalidad

# Cambiar a esa rama
git checkout feature/nueva-funcionalidad

# Hacer cambios y commits normales...

# Cuando esté lista, mezclar con main
git checkout main
git merge feature/nueva-funcionalidad
git push origin main
```

---

## 📋 Checklist semanal

Para mantener tu proyecto sano:

```
🟢 Cada vez que cambies código:
  [ ] Hago commit local (git commit)
  [ ] Subo a GitHub (git push)
  [ ] Bajo en PythonAnywhere (git pull)
  [ ] Recargo aplicación (Reload)
  [ ] Verifico en browser

🔵 Cada semana:
  [ ] Reviso logs de errores en PythonAnywhere → Error log tab
  [ ] Verifico que app esté funcionando
  [ ] Hago backup de BD si es crítico

🟣 Cada mes:
  [ ] Reviso git log para ver qué cambió
  [ ] Documento cambios en README si hay cambios importantes
  [ ] Verifico que no haya carpetas innecesarias
```

---

## 💾 Mejor práctica: Mensajes de commit

**MALO**:
```
git commit -m "cambios"
git commit -m "fix"
git commit -m "update"
```

**BUENO**:
```
git commit -m "Agregar filtro por categoría en dashboard"
git commit -m "Corregir error de timezone en reportes"
git commit -m "Actualizar estilos de botones en panel admin"
```

**Patrón recomendado**:
```
git commit -m "[TIPO] Descripción breve"

TIPOS:
- [FEATURE] Agregar nueva funcionalidad
- [FIX] Corregir bug
- [STYLE] Cambios de CSS
- [REFACTOR] Mejorar código
- [DOCS] Actualizar documentación
- [PERF] Optimización de performance

EJEMPLO:
git commit -m "[FEATURE] Agregar panel de usuarios"
git commit -m "[FIX] Corregir filtro de ventas"
git commit -m "[STYLE] Mejorar responsive design mobile"
```

---

## 🚨 Problemas comunes y soluciones

### Problema: "git push" pide contraseña

```bash
# Solución: Usar SSH en lugar de HTTPS
git remote set-url origin git@github.com:AzaeroDiego/InventarioApp.git
git push origin main
```

---

### Problema: "permission denied" en PythonAnywhere

```bash
# Solución: Regenerar SSH si es necesario
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
cat ~/.ssh/id_rsa.pub
# Copiar a GitHub → Settings → SSH Keys
```

---

### Problema: "Estoy en rama equivocada"

```bash
# Ver rama actual
git branch

# Cambiar a main
git checkout main

# Ver todas las ramas
git branch -a
```

---

### Problema: "Hice cambios que no quiero"

```bash
# Ver qué cambió
git status

# Descartar cambios en UN archivo
git checkout app/main.py

# Descartar TODO
git checkout .

# Si ya hiciste commit: revert (crea commit nuevo)
git revert HEAD --no-edit
```

---

## 📚 Ejemplo: Ciclo completo de un cambio

### Escenario: Agregar nueva página de reportes

**Paso 1: En tu PC**

```bash
# Cambiar a main y asegurar que está actualizado
git checkout main
git pull origin main

# Crear rama para feature nueva
git branch feature/nueva-pagina-reportes
git checkout feature/nueva-pagina-reportes

# Editar:
# - app/main.py (agregar ruta)
# - templates/main/reportes.html (crear plantilla)
# - static/css/style.css (agregar estilos)

# Ver cambios
git status

# Agregar cambios
git add .

# Commit
git commit -m "[FEATURE] Agregar página de reportes"

# Subir rama
git push origin feature/nueva-pagina-reportes
```

**Paso 2: En GitHub (OPCIONAL, para revisión)**

```
1. Abrir: https://github.com/AzaeroDiego/InventarioApp
2. Debería sugerir "Compare & pull request"
3. Click "Create pull request"
4. Revisar cambios
5. Click "Merge pull request"
```

(Esto es para equipos. Si trabajas solo, puedes mezclar en local)

**Paso 3: Mezclar en main (local)**

```bash
git checkout main
git merge feature/nueva-pagina-reportes

# Actualizar GitHub
git push origin main

# Limpiar rama
git branch -d feature/nueva-pagina-reportes
```

**Paso 4: En PythonAnywhere**

```bash
cd /home/AzaeroDiego/InventarioApp/InventarioApp
git pull origin main
```

**Paso 5: En Dashboard**

```
Reload
```

**Paso 6: Verificar en browser**

```
https://azaerodiego.pythonanywhere.com/reportes
```

✅ **Feature implementada**

---

## 🎯 Resumen: Comandos más usados

| Tarea | Comando |
|-------|---------|
| Ver qué cambió | `git status` |
| Agregar cambios | `git add .` |
| Guardar cambios | `git commit -m "mensaje"` |
| Subir a GitHub | `git push origin main` |
| Descargar desde GitHub | `git pull origin main` |
| Ver historial | `git log --oneline -5` |
| Deshacer cambios | `git checkout .` |
| Descargar branch nuevo | `git pull origin main` |

---

## 📖 Recursos adicionales

Si necesitas ayuda:

- **Git oficial**: https://git-scm.com/book/es
- **GitHub Docs**: https://docs.github.com
- **PythonAnywhere Help**: https://help.pythonanywhere.com
- **Archivo previo**: `GITHUB_PYTHONANYWHERE_FLUJO.md` (troubleshooting)

---

## ✨ Lo más importante

```
1. Haz commits frecuentes (no esperes a tener 20 cambios)
2. Escribe mensajes claros (no "fix" sino "Corregir X")
3. Siempre git pull antes de cambios nuevos
4. Siempre git push después de cambios
5. Recarga app en PythonAnywhere después de cambios
```

---

## 🎉 ¡Ya está!

Tu proyecto está configurado profesionalmente con:

- ✅ Versionado en GitHub
- ✅ Actualización fácil en PythonAnywhere
- ✅ Historial completo de cambios
- ✅ Rollback posible si algo falla
- ✅ Listo para colaboración futuro si necesitas

---

## Próximo paso

¿Quieres...?

- ⚙️ **Más automation**: Ver `PLAN_ACTUALIZACION_PRODUCCION.md`
- 📊 **Entender git mejor**: https://git-scm.com/book/es
- 🤝 **Trabajar en equipo**: Configura branches y pull requests
- 📚 **Volver a índice**: Ver `GITHUB_INDICE_DOCUMENTACION.md`

---

**¡Éxito con tu proyecto!** 🚀
