# Reconstrucción y administración de ventas

La pantalla Ventas abre el intervalo desde el 9 de agosto del año de referencia
hasta la fecha actual. El administrador puede cambiar libremente las fechas,
buscar productos/SKU/número de venta, filtrar por vendedor y consultar registros
vigentes, anulados o ambos. Los totales abarcan todas las ventas del intervalo;
la paginación de 25 filas no limita las sumas a los últimos 500 registros.

## Vistas

- Resumen: importe vigente, registros, unidades, días con registros, evolución,
  ranking de productos y ventas por hora local (America/Lima).
- Histórico y edición: detalle paginado, edición, anulación, restauración y auditoría.
- Reconstrucción: calendario del intervalo. Diferencia días con registros,
  registros reconstruidos y días sin registros. Los últimos no se consideran
  automáticamente días sin ventas ni jornadas en las que el negocio abrió.

## Añadir ventas antiguas

El administrador usa Añadir venta antigua e indica producto, fecha/hora real,
cantidad, precio, vendedor opcional, referencia de la fuente y motivo.
La referencia puede ser un comprobante, un resumen del día o el nombre de un
respaldo. El sistema etiqueta el registro como reconstruido; no genera ventas
supuestas ni rellena huecos automáticamente.

Por defecto estas entradas no modifican el stock actual. Existe una casilla
explícita para aplicar diferencias al stock cuando corresponda. Antes de usarla
deben revisarse las existencias actuales para evitar descontar ventas antiguas
que ya estén reflejadas en el inventario.

## Edición y borrado reversible

Solo una cuenta con rol admin y permiso de escritura puede modificar el histórico.
Las correcciones exigen motivo y conservan los valores anteriores y posteriores,
el usuario, la fecha y si afectaron al stock. Los otros usuarios solo consultan.

Anular funciona como borrado reversible: excluye la venta de los totales y del
resumen del panel, conserva la fila original y permite restaurarla. El administrador
puede elegir devolver o volver a descontar unidades del stock actual; esa decisión
queda auditada y está desmarcada por defecto. No hay borrado físico de ventas.

Las correcciones que afectan al stock se aplican en la misma transacción y no
permiten existencias negativas. Los reintentos de una misma solicitud no duplican
ventas ni eventos de auditoría.

## Exportación

Exportar período descarga todos los registros que coincidan con los filtros,
incluyendo estado, origen y referencia. El límite por archivo es de 10.000 filas;
si el intervalo lo supera se pide reducirlo, sin exportar resultados truncados.

## Instalación y pruebas

`supabase/migrations/20261024_sales_history.sql` añade únicamente estado reversible,
auditoría y funciones protegidas, y adapta el panel existente para excluir anuladas.
La instalación no modifica ventas, productos ni cantidades existentes. Se conserva
la primera función de lectura como helper privado, sin acceso desde el navegador.

`npm test` incluye 29 comprobaciones previas y 28 de histórico en PostgreSQL WASM
aislado. Cubre más de 500 ventas, fechas nocturnas, paginación, reconstrucción sin
cambiar stock, edición, anulación/restauración, stock opcional, auditoría,
idempotencia y rechazo de modificaciones de usuarios no administradores.

El historial de auditoría empieza con esta actualización. No se fabrica una
auditoría retrospectiva para acciones realizadas antes de su instalación.
