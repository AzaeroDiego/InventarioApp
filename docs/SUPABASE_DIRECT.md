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
- La instalación de las nuevas funciones fue autorizada y realizada el 24 de octubre de 2026.
  Se comprobó que no cambiara la cantidad de registros de las once tablas del negocio.
  La API pública devuelve 401 a llamadas anónimas de lectura y escritura.

## Acceso sin cambiar las contraseñas existentes

La nueva web ofrece contraseña de Supabase Auth o enlace por correo. Para el primer
acceso se usa el mismo correo que ya figura en `inventario.usuarios` y se verifica
la propiedad de ese correo. No se envían contraseñas antiguas ni hashes al navegador.
Los usuarios nuevos de Auth sin correspondencia activa en el inventario no reciben acceso.
Cada operación comprueba el estado y los permisos actuales, sin confiar en el frontend.

En Supabase → Authentication → URL Configuration se añade únicamente:

```text
Redirect URLs: https://azaerodiego.github.io/InventarioApp/
```

Se conserva la Site URL predeterminada de CuentasPersonales y su redirect existente,
porque el mismo proyecto de Supabase se comparte con esa otra aplicación.
La nueva web envía su destino explícitamente mediante `redirect_to`.
Para pruebas locales puede añadirse temporalmente `http://127.0.0.1:5178/`.
No se enviaron correos de acceso durante
el desarrollo. Si los correos se bloquean por límites del proveedor de correo
compartido de Supabase, debe configurarse el envío para los usuarios del proyecto.

## Instalación SQL autorizada

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
Posteriormente el usuario autorizó instalar el script. La instalación se realizó
en una única transacción y verificó los permisos antes de confirmar los cambios.

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

## Publicación

La web está publicada en `https://azaerodiego.github.io/InventarioApp/`.
El despliegue `Publish Stock Studio` terminó correctamente el 24 de octubre de 2026.
GitHub Pages usa GitHub Actions y el flujo `pages.yml` publica `web/` al integrar cambios
de la interfaz en `main`. Se verificó que el sitio público muestra la pantalla de acceso.
La prueba de acceso real mediante correo corresponde al usuario; no se crean identidades
ficticias en producción ni se solicitan contraseñas privadas para validarla.
La clave publishable de `web/config.js` es pública por diseño. No deben añadirse
contraseñas PostgreSQL, claves secretas ni `service_role` al código ni a Pages.

Las credenciales privadas que se compartieron en el chat deben renovarse antes de
publicar. La nueva conexión directa no necesita esas credenciales para funcionar.
