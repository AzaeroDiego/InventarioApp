# Stock Studio — alternativa de compatibilidad con Flask

**La arquitectura elegida ahora es GitHub Pages → Supabase, sin Render.**
Consulta [SUPABASE_DIRECT.md](SUPABASE_DIRECT.md) para la implementación actual.
Lo siguiente documenta la alternativa inicial con Flask, que permanece disponible
para compatibilidad y no es la conexión predeterminada de la nueva web.

## Qué cambia

`web/` contiene una aplicación estática, adaptable a móvil, que abre sin arrancar Flask.
Incluye resumen, inventario con búsqueda/filtros/paginación, creación de productos,
entradas y salidas, ventas, alertas y exportación CSV. El modo de muestra es explícito,
no guarda cambios y no accede a datos reales. Los registros de ventas y movimientos se
limitan a 500 por vista; el gráfico agrega todas las ventas de los últimos siete días.

Barra, lotes, categorías, vendedores, usuarios y reportes completos siguen en Flask.
Se abren con un pase firmado de 30 segundos y conservan sus funciones y permisos
actuales. Las plantillas existentes reciben una base visual nueva.

## PostgreSQL se conserva

No hay migración ni copia de datos. Se conserva `DATABASE_URL` y el esquema `inventario`.
La producción rechaza la ausencia de PostgreSQL y una clave de sesión predeterminada.
SQLite queda exclusivamente para desarrollo y pruebas aisladas.
`AUTO_CREATE_TABLES=false` es el valor de producción para evitar operaciones de creación
de tablas en cada arranque. El esquema existente debe estar creado previamente.

En el servicio Python existente, conservar/configurar variables privadas:

```text
FLASK_ENV=production
DATABASE_URL=<la conexión PostgreSQL existente>
SECRET_KEY=<la clave privada existente, no la predeterminada>
PAGES_ORIGIN=https://azaerodiego.github.io
AUTO_CREATE_TABLES=false
```

No colocar ninguna de estas credenciales en el frontend ni en el repositorio.
`PAGES_ORIGIN` es un origen, sin ruta ni barra final; CORS no admite comodines.
La URL pública del servidor es lo único que se configura en `web/config.js`:

```javascript
window.STOCK_CONFIG = { API_BASE: 'https://tu-servicio.example.com' };
```

También se puede introducir esa dirección en la pantalla de acceso. No es la dirección
de PostgreSQL. La autenticación usa los usuarios actuales del inventario y un token
firmado que vence a las ocho horas, conservado solo durante la sesión del navegador.
Se comprueba que el usuario siga activo y tenga permiso de escritura en cada operación.
No se habilita registro público nuevo en esta API.

## Publicar en GitHub Pages

1. Instalar primero los cambios del servidor en el servicio Python, conservando su base de datos.
2. Configurar la URL pública anterior en `web/config.js`.
3. En Settings → Pages del repositorio, elegir GitHub Actions como fuente.
4. Integrar los cambios de `web/` y el flujo `.github/workflows/pages.yml` en `main`.
5. Revisar el despliegue `Publish Stock Studio`. La dirección prevista, pendiente de
   confirmación del despliegue, es `https://azaerodiego.github.io/InventarioApp/`.

La interfaz también está disponible en `/workspace/` en el servidor Flask.
La interfaz antigua sigue disponible en sus rutas actuales.

## Sobre la espera al entrar

GitHub Pages sirve HTML, CSS y JavaScript estáticos; no ejecuta Flask ni PostgreSQL.
Separar la interfaz evita esperar para dibujar la pantalla, pero **no despierta ni acelera
un servidor suspendido**. Si el alojamiento gratuito apaga el backend, seguirá existiendo
una espera para iniciar sesión y consultar datos. La interfaz informa del fallo tras
15 segundos en vez de esperar indefinidamente. La conexión PostgreSQL tiene un límite
de ocho segundos por intento; eso no es un límite global del arranque de la plataforma.

Para eliminar la espera del backend hace falta un alojamiento que no suspenda el
servicio, o migrar la API a otro entorno. La URL/proveedor actual todavía debe
identificarse antes de elegir esa solución. Ningún cambio de alojamiento se ha realizado.

## Referencias y REA

Se eligió Sortly por la organización accesible del inventario y sus estados de stock,
y se consultó inFlow por la jerarquía del panel y sus resúmenes operativos:

- https://help.sortly.com/sortly-product-overview
- https://www.inflowinventory.com/support/cloud/dashboard

Se ejecutó REA 6.7.0 (`morluto/rea`, paquete `rea-agents`) contra una captura local
del HTML público de Sortly y su `main.js` público. REA produjo un inventario parcial
de archivos y referencias de scripts, pero el análisis JavaScript completo falló:
`REA Windows native self-test failed ... Open Windows path component ... Win32 5`.
El intento se repitió tras conceder lectura de la ruta y falló del mismo modo.
Por tanto, no se afirma haber reconstruido la aplicación privada de Sortly ni sus
reglas internas. El diseño y la implementación son nuevos; no se redistribuye su código.

## Validación

```text
node --check web/studio.js
python -m unittest discover -s tests -v
```

Las pruebas aíslan una base temporal en memoria y nunca usan PostgreSQL de producción.
Cubren acceso, CORS, permisos de lectura, validación, SKU duplicado, actualización
atómica del stock, venta con stock insuficiente y acceso a las herramientas conservadas.
La validación en PostgreSQL de producción y la demora real quedan pendientes de acceso
al servicio actual. No se tocaron datos de producción.
