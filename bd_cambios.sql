--En la bd de contabilidad
CREATE TABLE ventas_contables (
    id SERIAL PRIMARY KEY,
    id_detalle INT NOT NULL,
    id_pedido INT NOT NULL,
    id_usuario INT NOT NULL,
    fecha TIMESTAMP NOT NULL,
    id_producto INT NOT NULL,
    nombre_producto VARCHAR(255) NOT NULL,
    cantidad INT NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL
);

mysql, ventas:
ALTER TABLE pedidos ADD COLUMN registrado_en_contable BOOLEAN DEFAULT FALSE;