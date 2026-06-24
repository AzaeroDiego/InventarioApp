# 📚 ÍNDICE DE DOCUMENTACIÓN — GitHub + PythonAnywhere

**Última actualización**: 15 de Marzo de 2026

---

## 🎯 ¿CUÁL DOCUMENTO LEO PRIMERO?

### Si estás corriendo contra el tiempo ⏱️
→ **`GITHUB_SETUP_CHECKLIST.md`**
- 12 pasos simples, copiar-pegar
- Checklist interactivo
- ~15 minutos

---

### Si quieres entender bien qué estás haciendo 📖
→ **`GITHUB_PYTHONANYWHERE_FLUJO.md`**
- Explicación completa
- Por qué funciona así
- Troubleshooting detallado
- ~30 minutos de lectura

---

### Si quieres la referencia histórica de cómo se subió ZIP 🏛️
→ **`PYTHONANYWHERE_DESPLIEGUE_PASO_A_PASO.md`**
- Método antiguo (ZIP manual)
- Por qué cambiar a GitHub
- Ahora con sección NEW sobre GitHub
- ~20 minutos

---

### Si necesitas entender la estrategia general 🎯
→ **`PLAN_ACTUALIZACION_PRODUCCION.md`**
- Cuáles archivos suben
- Qué migraciones ejecutar
- Cómo hacer rollback
- Procedimiento de validación

---

### Si prefieres manual sin automatización 🛠️
→ **`GUIA_DESPLIEGUE_PASO_A_PASO.md`**
- Cada paso explicado
- Bash commands desagregados
- Verificación de cada paso

---

## 📊 TABLA COMPARATIVA

| Documento | Público | Detalle | Tiempo | Para quién |
|-----------|---------|---------|---------|-----------|
| **GITHUB_SETUP_CHECKLIST.md** | ✅ | ⭐⭐⭐ | 15 min | Quiero hacerlo YA |
| **GITHUB_PYTHONANYWHERE_FLUJO.md** | ✅ | ⭐⭐⭐⭐⭐ | 30 min | Quiero aprender |
| **PYTHONANYWHERE_DESPLIEGUE_PASO_A_PASO.md** | ✅ | ⭐⭐⭐⭐ | 25 min | Referencia método antiguo |
| **PLAN_ACTUALIZACION_PRODUCCION.md** | ✅ | ⭐⭐⭐ | 10 min | Quiero estrategia |
| **GUIA_DESPLIEGUE_PASO_A_PASO.md** | ✅ | ⭐⭐⭐⭐ | 20 min | Prefiero manual |

---

## 🚀 FLUJO RECOMENDADO (SI ERES NUEVO EN GIT)

```
1️⃣  Leer: GITHUB_SETUP_CHECKLIST.md (entender qué hacer)
     ↓
2️⃣  Leer: GITHUB_PYTHONANYWHERE_FLUJO.md (sections 1-4, entender por qué)
     ↓
3️⃣  Ejecutar: Los pasos del checklist
     ↓
4️⃣  Verificar: Que todo funcione en https://azaerodiego.pythonanywhere.com
     ↓
5️⃣  Guardar: GITHUB_PYTHONANYWHERE_FLUJO.md para futuras actualizaciones
```

**Tiempo total**: ~45 minutos

---

## 🔧 FLUJO RÁPIDO (SI CONOCES GIT)

```
1️⃣  Ejecutar: Pasos de GITHUB_SETUP_CHECKLIST.md
     ↓
2️⃣  Si hay error → Mirar "Troubleshooting" en GITHUB_PYTHONANYWHERE_FLUJO.md
     ↓
3️⃣  Verificar en browser
```

**Tiempo total**: ~15 minutos

---

## 📋 ARCHIVOS DEL PROYECTO

### Nuevos (Marzo 2026)
```
✅ GITHUB_SETUP_CHECKLIST.md              ← EMPIEZA AQUÍ
✅ GITHUB_PYTHONANYWHERE_FLUJO.md         ← Guía completa
✅ GITHUB_INDICE_DOCUMENTACION.md         ← Este archivo
```

### Anteriores (para referencia)
```
📄 PYTHONANYWHERE_DESPLIEGUE_PASO_A_PASO.md  (actualizado)
📄 PLAN_ACTUALIZACION_PRODUCCION.md
📄 GUIA_DESPLIEGUE_PASO_A_PASO.md
```

### De proyecto (código actual)
```
✅ app/
✅ templates/main/admin_usuarios.html (nuevo)
✅ migrate_db.py (nuevo)
✅ migrate_permisos.py (nuevo)
✅ config.py (actualizado)
✅ app/models.py (actualizado)
✅ app/main.py (actualizado)
✅ templates/base.html (actualizado)
```

---

## 🎓 CONCEPTOS CLAVE

### GitHub
- Repositorio donde guardas el código con historial
- Puede ser público o privado
- Acceso: https://github.com/AzaeroDiego/InventarioApp

### SSH Keys
- Forma segura para que PythonAnywhere acceda a GitHub
- Sin contraseña cada vez
- Genera par: clave privada (PythonAnywhere) + clave pública (GitHub)

### Git Clone
- Descarga el repositorio desde GitHub a PythonAnywhere
- Crea carpeta `.git` para historial

### Git Pull
- Actualización simple: descarga cambios nuevos
- En PythonAnywhere: 1 comando

### Migraciones
- Scripts que actualizan la base de datos
- `migrate_db.py` → agrega columna `se_vende`
- `migrate_permisos.py` → agrega columnas `has_permisos` y `rol`

---

## ✅ CHECKLIST PREVIO

Antes de empezar, tener listo:

- [ ] Cuenta en GitHub creada (https://github.com)
- [ ] Acceso a PythonAnywhere funcional
- [ ] Credenciales para ambas cuentas
- [ ] Navegador para verificación
- [ ] ~15-30 minutos de tiempo

---

## 🔗 ENLACES RÁPIDOS

| Recurso | URL |
|---------|-----|
| **GitHub** | https://github.com |
| **Tu repo** | https://github.com/AzaeroDiego/InventarioApp |
| **PythonAnywhere** | https://www.pythonanywhere.com/user/AzaeroDiego/ |
| **Tu app** | https://azaerodiego.pythonanywhere.com |
| **SSH Keys GitHub** | https://github.com/settings/keys |

---

## 💡 CONSEJOS

1. **Lee el checklist primero** → Te ahorra preguntas
2. **Copia-pega comandos** → Menos errores que escribir
3. **Verifica cada paso** → No esperes al final
4. **Guarda estos documentos** → Los necesitarás después
5. **Git pull es tu amigo** → Úsalo cada vez que actualices

---

## 🚨 SI ALGO FALLA

### Paso 1: Verificar error
```bash
# Saca el mensaje de error completo
# Que sea lo más específico posible
```

### Paso 2: Buscar en documento
Busca el error en:
- `GITHUB_PYTHONANYWHERE_FLUJO.md` → Sección "Troubleshooting"
- `GITHUB_SETUP_CHECKLIST.md` → Sección "Si algo falla"

### Paso 3: Si sigue sin funcionar
Documenta:
- ¿En qué paso falló?
- ¿Cuál fue exactamente el error?
- ¿Qué comando ejecutaste?

---

## 🎯 TU PRÓXIMO PASO

**Ahora eliges:**

### Opción A: Aprender bien (recomendado)
→ Lee: `GITHUB_PYTHONANYWHERE_FLUJO.md`

### Opción B: Hacerlo rápido
→ Ve al: `GITHUB_SETUP_CHECKLIST.md`

### Opción C: Entender todo
→ Lee todos en este orden:
1. GITHUB_SETUP_CHECKLIST.md
2. GITHUB_PYTHONANYWHERE_FLUJO.md
3. PLAN_ACTUALIZACION_PRODUCCION.md

---

**Última actualización**: 15 de Marzo de 2026  
**Versión**: 2.1.1  
**Estado**: ✅ Listo para usar

---

¿Dudas? Revisa el documento que corresponda a tu nivel.

¡Vamos! 🚀
