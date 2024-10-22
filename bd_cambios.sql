--En la bd de contabilidad
CREATE TABLE ventas_contables (
    id SERIAL PRIMARY KEY,
    id_detalle INT NOT NULL,
    id_pedido INT NOT NULL,
    id_usuario INT NOT NULL,
	usuario VARCHAR(255) NOT NULL,
    fecha TIMESTAMP NOT NULL,
    id_producto INT NOT NULL,
    nombre_producto VARCHAR(255) NOT NULL,
    cantidad INT NOT NULL,
    sub_sin_igv NUMERIC(10, 2) NOT NULL,
    igv NUMERIC(10, 2) NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL,
    serie_comprobante VARCHAR(10) NOT NULL,
    numero_comprobante VARCHAR(10) NOT NULL
);