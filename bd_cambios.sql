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

CREATE TABLE movimientos (
    movimiento_id VARCHAR(30) PRIMARY KEY,
    fecha TIMESTAMP NOT NULL,
    tipo_comprobante VARCHAR(20) NOT NULL,
    serie_comprobante VARCHAR(10) NOT NULL,
    numero_comprobante VARCHAR(10) NOT NULL,
    tipo_documento VARCHAR(20) NOT NULL,
    numero_documento VARCHAR(30) NOT NULL,
    entidad VARCHAR(255) NOT NULL,
    tipo_movimiento VARCHAR(10) NOT NULL CHECK (tipo_movimiento IN ('Ventas', 'Compras')),
    sub_sin_igv NUMERIC(10, 2) NOT NULL,
    igv NUMERIC(10, 2) NOT NULL,
    total NUMERIC(10, 2) NOT NULL
);

------------------------------------------------------------------

--Consulta para unir ambas tablas:
SELECT
    CONCAT('V-', v.serie_comprobante, v.numero_comprobante) AS movimiento_id,
    v.fecha AS fecha,
    v.tipo_comprobante AS tipo_comprobante,
    v.serie_comprobante AS serie_comprobante,
    v.numero_comprobante AS numero_comprobante,
    v.tipo_documento AS tipo_documento,
    v.numero_documento AS numero_documento,
    v.usuario AS entidad,
    'Ventas' AS tipo_movimiento,
    v.sub_sin_igv AS sub_sin_igv,
    v.igv AS igv,
    v.total AS total
FROM ventas_contables v

UNION ALL

SELECT
    CONCAT('C-', c.serie_comprobante, c.numero_comprobante) AS movimiento_id,
    c.fecha AS fecha,
    c.tipo_comprobante AS tipo_comprobante,
    c.serie_comprobante AS serie_comprobante,
    c.numero_comprobante AS numero_comprobante,
    c.tipo_documento AS tipo_documento,
    c.numero_documento AS numero_documento,
    c.nombre_proveedor AS entidad,
    'Compras' AS tipo_movimiento,
    c.sub_sin_igv AS sub_sin_igv,
    c.igv AS igv,
    c.total AS total
FROM compras_contables c

ORDER BY fecha, serie_comprobante, numero_comprobante;