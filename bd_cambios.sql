--En la bd de contabilidad
CREATE TABLE ventas_contables (
    id SERIAL PRIMARY KEY,
    --id_detalle INT NOT NULL,
    id_pedido INT NOT NULL,
    id_usuario INT NOT NULL,
	usuario VARCHAR(255) NOT NULL,
    tipo_documento VARCHAR(20) NOT NULL,
    numero_documento VARCHAR(30) NOT NULL,
    fecha TIMESTAMP NOT NULL,
    --id_producto INT NOT NULL,
    --nombre_producto VARCHAR(255) NOT NULL,
    --cantidad INT NOT NULL,
    sub_sin_igv NUMERIC(10, 2) NOT NULL,
    igv NUMERIC(10, 2) NOT NULL,
    total NUMERIC(10, 2) NOT NULL,
    tipo_comprobante VARCHAR(20) NOT NULL,
    serie_comprobante VARCHAR(10) NOT NULL,
    numero_comprobante VARCHAR(10) NOT NULL
);

CREATE TABLE compras_contables (
    id SERIAL PRIMARY KEY,
    --id_detalle_compra INT NOT NULL,
    id_compra INT NOT NULL,
    id_usuario INT NOT NULL,
    usuario VARCHAR(255) NOT NULL,
    id_proveedor INT NOT NULL,
    nombre_proveedor VARCHAR(255) NOT NULL,
    tipo_documento VARCHAR(20) NOT NULL,
    numero_documento VARCHAR(30) NOT NULL,
    fecha TIMESTAMP NOT NULL,
    --id_insumo INT NOT NULL,
    --nombre_insumo VARCHAR(255) NOT NULL,
    --cantidad INT NOT NULL,
    sub_sin_igv NUMERIC(10, 2) NOT NULL,
    igv NUMERIC(10, 2) NOT NULL,
    total NUMERIC(10, 2) NOT NULL,
    tipo_comprobante VARCHAR(20) NOT NULL,
    serie_comprobante VARCHAR(10) NOT NULL,
    numero_comprobante VARCHAR(10) NOT NULL
);