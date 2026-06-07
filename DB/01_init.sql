CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    rut VARCHAR(12) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(80) NOT NULL,
    apellido VARCHAR(80) NOT NULL,
    rol VARCHAR(10) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    Fecha_nacimiento DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    rut_empresa NUMERIC(9, 0) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    familia VARCHAR(80) NOT NULL,
    subfamilia VARCHAR(80),
    descripcion TEXT NOT NULL,
    PN VARCHAR(80),
    serie VARCHAR(5)
);

CREATE TABLE IF NOT EXISTS cliente_contacto (
    id SERIAL PRIMARY KEY,
    id_cliente INT REFERENCES clientes(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    telefono VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS ventas (
    COT NUMERIC(5, 0) PRIMARY KEY,
    id_cliente INT REFERENCES clientes(id) ON DELETE CASCADE,
    fecha_creacion TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(10) DEFAULT "COTIZADO",
    fecha_cot DATE,
    orden_de_compra VARCHAR(12),
    fecha_oco DATE,
    nota_de_venta NUMERIC(5, 0)
);

CREATE TABLE IF NOT EXISTS venta_detalle (
    id_venta NUMERIC(5, 0) REFERENCES ventas(COT) ON DELETE CASCADE,
    id_producto INT REFERENCES productos(id) ON DELETE CASCADE,
    cantidad INT NOT NULL,
    precio_unitario INT NOT NULL,
    PRIMARY KEY (id_venta, id_producto)
);

CREATE TABLE IF NOT EXISTS facturas (
    NFAC NUMERIC(6, 0) PRIMARY KEY,
    id_venta NUMERIC(5, 0) REFERENCES ventas(COT) ON DELETE CASCADE,
    fecha_emision DATE NOT NULL,
    estado VARCHAR(10) DEFAULT "PENDIENTE"
);

CREATE TABLE IF NOT EXISTS factura_detalle (
    NFAC NUMERIC(6, 0) REFERENCES facturas(NFAC) ON DELETE CASCADE,
    id_producto INT REFERENCES productos(id) ON DELETE CASCADE,
    cantidad INT NOT NULL,
    PRIMARY KEY (id_factura, id_producto)
);

CREATE TABLE IF NOT EXISTS guia_despacho (
    numero_guia NUMERIC(4, 0) PRIMARY KEY,
    id_venta NUMERIC(5, 0) REFERENCES ventas(COT) ON DELETE CASCADE,
    fecha_despacho DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS guia_detalle (
    numero_guia NUMERIC(4, 0) REFERENCES guia_despacho(numero_guia) ON DELETE CASCADE,
    id_producto INT REFERENCES productos(id) ON DELETE CASCADE,
    cantidad INT NOT NULL,
    PRIMARY KEY (id_guia, id_producto)
);