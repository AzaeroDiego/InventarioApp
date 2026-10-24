CREATE SCHEMA inventario; CREATE SCHEMA auth; CREATE ROLE anon; CREATE ROLE authenticated;
CREATE TABLE auth.users(id uuid PRIMARY KEY,email text,email_confirmed_at timestamptz);
CREATE FUNCTION auth.uid() RETURNS uuid LANGUAGE sql STABLE AS $$ SELECT nullif(current_setting('request.jwt.claim.sub',true),'')::uuid $$;

CREATE TABLE inventario.usuarios (
	id SERIAL NOT NULL, 
	nombre_completo VARCHAR(120) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	has_permisos BOOLEAN, 
	rol VARCHAR(50), 
	activo BOOLEAN, 
	fecha_creacion TIMESTAMP WITHOUT TIME ZONE, 
	fecha_actualizacion TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
)

;
CREATE UNIQUE INDEX ix_inventario_usuarios_email ON inventario.usuarios (email);

CREATE TABLE inventario.categorias (
	id SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	color VARCHAR(7), 
	descripcion TEXT, 
	activa BOOLEAN, 
	fecha_creacion TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (nombre)
)

;

CREATE TABLE inventario.vendedores (
	id SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	email VARCHAR(100), 
	telefono VARCHAR(20), 
	comision_porcentaje FLOAT, 
	activo BOOLEAN, 
	fecha_creacion TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (nombre), 
	UNIQUE (email)
)

;

CREATE TABLE inventario.productos (
	id SERIAL NOT NULL, 
	nombre VARCHAR(150) NOT NULL, 
	sku VARCHAR(50) NOT NULL, 
	categoria_id INTEGER NOT NULL, 
	descripcion TEXT, 
	precio FLOAT NOT NULL, 
	cantidad_stock INTEGER, 
	stock_minimo INTEGER, 
	litros_por_unidad FLOAT, 
	imagen_url VARCHAR(255), 
	codigo_qr VARCHAR(255), 
	se_vende BOOLEAN, 
	activo BOOLEAN, 
	fecha_creacion TIMESTAMP WITHOUT TIME ZONE, 
	fecha_actualizacion TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(categoria_id) REFERENCES inventario.categorias (id)
)

;
CREATE INDEX ix_inventario_productos_nombre ON inventario.productos (nombre);
CREATE UNIQUE INDEX ix_inventario_productos_sku ON inventario.productos (sku);

CREATE TABLE inventario.lotes (
	id SERIAL NOT NULL, 
	nombre VARCHAR(200) NOT NULL, 
	descripcion TEXT, 
	cantidad_preparada INTEGER NOT NULL, 
	cantidad_vendida INTEGER, 
	costo_total FLOAT NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	fecha_preparacion TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES inventario.usuarios (id)
)

;

CREATE TABLE inventario.controles_barra (
	id SERIAL NOT NULL, 
	fecha_operacion DATE NOT NULL, 
	hora_cierre VARCHAR(20), 
	usuario_id INTEGER NOT NULL, 
	responsable_id INTEGER NOT NULL, 
	observaciones TEXT, 
	total_esperado FLOAT NOT NULL, 
	monto_entregado FLOAT NOT NULL, 
	diferencia_caja FLOAT NOT NULL, 
	fecha_creacion TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES inventario.usuarios (id), 
	FOREIGN KEY(responsable_id) REFERENCES inventario.usuarios (id)
)

;
CREATE INDEX ix_inventario_controles_barra_fecha_creacion ON inventario.controles_barra (fecha_creacion);

CREATE TABLE inventario.movimientos_stock (
	id SERIAL NOT NULL, 
	producto_id INTEGER NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	tipo VARCHAR(20) NOT NULL, 
	cantidad INTEGER NOT NULL, 
	motivo VARCHAR(200), 
	observaciones TEXT, 
	fecha TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(producto_id) REFERENCES inventario.productos (id), 
	FOREIGN KEY(usuario_id) REFERENCES inventario.usuarios (id)
)

;
CREATE INDEX ix_inventario_movimientos_stock_fecha ON inventario.movimientos_stock (fecha);

CREATE TABLE inventario.alertas_stock (
	id SERIAL NOT NULL, 
	producto_id INTEGER NOT NULL, 
	tipo VARCHAR(50), 
	mensaje VARCHAR(255), 
	leida BOOLEAN, 
	fecha_creacion TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(producto_id) REFERENCES inventario.productos (id)
)

;

CREATE TABLE inventario.ventas (
	id SERIAL NOT NULL, 
	producto_id INTEGER NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	vendedor_id INTEGER, 
	lote_id INTEGER, 
	cantidad INTEGER NOT NULL, 
	precio_unitario FLOAT NOT NULL, 
	total FLOAT NOT NULL, 
	motivo VARCHAR(100), 
	observaciones TEXT, 
	fecha TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(producto_id) REFERENCES inventario.productos (id), 
	FOREIGN KEY(usuario_id) REFERENCES inventario.usuarios (id), 
	FOREIGN KEY(vendedor_id) REFERENCES inventario.vendedores (id), 
	FOREIGN KEY(lote_id) REFERENCES inventario.lotes (id)
)

;

CREATE TABLE inventario.ingredientes_lote (
	id SERIAL NOT NULL, 
	lote_id INTEGER NOT NULL, 
	producto_id INTEGER NOT NULL, 
	cantidad_usada FLOAT NOT NULL, 
	costo_unitario FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(lote_id) REFERENCES inventario.lotes (id), 
	FOREIGN KEY(producto_id) REFERENCES inventario.productos (id)
)

;

CREATE TABLE inventario.detalle_controles_barra (
	id SERIAL NOT NULL, 
	control_id INTEGER NOT NULL, 
	producto VARCHAR(150) NOT NULL, 
	stock_inicial INTEGER NOT NULL, 
	stock_final INTEGER NOT NULL, 
	vendidos INTEGER NOT NULL, 
	precio_unitario FLOAT NOT NULL, 
	total_esperado FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(control_id) REFERENCES inventario.controles_barra (id)
)

;