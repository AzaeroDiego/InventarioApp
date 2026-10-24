# GitHub Pages → Supabase: implementación directa

La interfaz utiliza la clave **pública publishable** del proyecto y Supabase Auth.
No llama a Render para iniciar sesión ni para operar el inventario. La aplicación
Flask anterior se conserva como alternativa, pero no es la ruta predeterminada.

## Estado verificado

- La conexión a PostgreSQL se comprobó en modo de solo lectura.
- Existe el esquema `inventario` con las tablas de productos, categorías, ventas,
  movimientos de stock, lotes, ingredientes, vendedores, usuarios y cierres de barra.
- Hay dos usuarios de inventario activos. El usuario de Supabase Auth existente
  no coincide con sus correos verificados; son dos sistemas de acceso distintos.
- La clave pública funciona. Supabase tiene el acceso por correo habilitado y
  requiere confirmación de correo.
- No se migraron, actualizaron ni borraron filas de producción.
- La instalación de las nuevas funciones en producción está pendiente de autorización.

## Acceso sin cambiar las contraseñas existentes

La nueva web ofrece contraseña de Supabase Auth o enlace por correo. Para el primer
acceso se usa el mismo correo que ya figura en `inventario.usuarios` y se verifica
la propiedad de ese correo. No se envían contraseñas antiguas ni hashes al navegador.
Los usuarios nuevos de Auth sin correspondencia activa en el inventario no reciben acceso.
Cada operación comprueba el estado y los permisos actuales, sin confiar en el frontend.

En Supabase → Authentication → URL Configuration se debe añadir:

```text
Site URL: https://azaerodiego.github.io/InventarioApp/
Redirect URLs: https://azaerodiego.github.io/InventarioApp/
```

Para pruebas locales puede añadirse temporalmente `http://127.0.0.1:5178/`.
No se han cambiado esas opciones todavía. No se enviaron correos de acceso durante
el desarrollo. Si los correos se bloquean por límites del proveedor de correo
compartido de Supabase, debe configurarse el envío para los usuarios del proyecto.

## Instalación SQL que requiere autorización

El archivo `supabase/migrations/20261024_stock_studio.sql` crea:

1. `stock_studio_private`, esquema interno sin permisos para el navegador.
2. `stock_studio_private.requests`, registro de operaciones para evitar duplicados.
3. Helpers internos para comprobar identidad y validar importes.
4. Dos funciones públicas: `stock_studio_data()` y `stock_studio_write(...)`.

Estas dos funciones solo se pueden ejecutar como `authenticated`. Los anónimos
no tienen acceso. La identidad se comprueba con `auth.uid()`, el correo confirmado
de `auth.users` y el usuario activo correspondiente en `inventario.usuarios`.
Las funciones usan `SECURITY DEFINER` con `search_path` vacío y referencias explícitas.
No se concede acceso directo a tablas ni se expone el esquema `inventario` en la API.
No se toca la tabla ajena `inventario.movimientos`.

El script no migra ni modifica filas de negocio al instalarse. Las escrituras
solo se producen después, cuando un usuario autorizado confirma una acción en la web.
El registro interno de solicitudes guarda el actor, la operación, sus datos y el resultado.

Una prueba transaccional en producción fue rechazada por revisión automática.
No se ejecutó. En su lugar, las funciones se verificaron en PostgreSQL WASM local,
sin red ni credenciales, con tablas y usuarios ficticios.

## Funciones de la interfaz

- Resumen y gráfico de ventas con agregados completos de los últimos siete días.
- Productos: crear y editar nombre, SKU, categoría, descripción, precio, mínimo y uso.
- Entradas y salidas; ajustes que establecen el stock contado, con motivo obligatorio.
- Ventas con vendedor opcional, descuento atómico de existencias y alertas.
- Categorías y vendedores: creación y edición.
- Lotes: consumen ingredientes y aumentan el stock del producto final en una transacción.
- Cierres de barra: conteo, monto entregado y diferencia, independientes del stock principal.
- Usuarios existentes: activar/desactivar y editar permisos y rol. No se permite
  modificar el propio acceso. No se cambian contraseñas desde esta interfaz.
- Exportación CSV con protección contra fórmulas introducidas como texto.

Los listados muestran hasta 500 ventas y movimientos recientes y 200 lotes/cierres.
Los ingredientes de los lotes se registran en unidades enteras porque el stock principal
existente es entero; no se redondean cantidades fraccionarias silenciosamente.
El modo de muestra utiliza datos ficticios, no guarda cambios y no accede a producción.

## Validación local

```text
npm ci
npm test
python -m unittest discover -s tests -v
```

`npm test` valida la sintaxis de los tres archivos JavaScript y ejecuta 29 comprobaciones
en PostgreSQL WASM: autenticación, correo ajeno, permisos, rechazo de anónimos, valores
inválidos, SKU duplicado, creación/edición de productos, entradas, ventas, stock
insuficiente, ajustes a cero, lotes, cierres independientes e idempotencia.
Las seis pruebas Python validan la ruta alternativa de Flask con una base aislada.

## Publicación pendiente

El repositorio no tiene GitHub Pages habilitado. El flujo `pages.yml` publica `web/`
al integrarse en `main`, una vez elegida GitHub Actions en Settings → Pages.
La clave publishable de `web/config.js` es pública por diseño. No deben añadirse
contraseñas PostgreSQL, claves secretas ni `service_role` al código ni a Pages.

Las credenciales privadas que se compartieron en el chat deben renovarse antes de
publicar. La nueva conexión directa no necesita esas credenciales para funcionar.
