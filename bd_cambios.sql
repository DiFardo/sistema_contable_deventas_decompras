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

------------------------------------------------
--permisos y roles:
CREATE TABLE IF NOT EXISTS public.roles
(
    id integer NOT NULL DEFAULT nextval('roles_id_seq'::regclass),
    nombre character varying(50) COLLATE pg_catalog."default" NOT NULL,
    descripcion text COLLATE pg_catalog."default",
    estado boolean DEFAULT true,
    CONSTRAINT roles_pkey PRIMARY KEY (id),
    CONSTRAINT roles_nombre_key UNIQUE (nombre)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.roles
    OWNER to avnadmin;

CREATE TABLE IF NOT EXISTS public.personas
(
    id integer NOT NULL DEFAULT nextval('personas_id_seq'::regclass),
    nombre character varying(50) COLLATE pg_catalog."default" NOT NULL,
    apellido character varying(50) COLLATE pg_catalog."default" NOT NULL,
    dni character varying(8) COLLATE pg_catalog."default" NOT NULL,
    imagen character varying(255) COLLATE pg_catalog."default",
    id_rol integer,
    CONSTRAINT personas_pkey PRIMARY KEY (id),
    CONSTRAINT personas_dni_key UNIQUE (dni),
    CONSTRAINT fk_roles FOREIGN KEY (id_rol)
        REFERENCES public.roles (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET NULL
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.personas
    OWNER to avnadmin;

CREATE TABLE IF NOT EXISTS public.usuarios
(
    id integer NOT NULL DEFAULT nextval('usuarios_id_seq'::regclass),
    dni character varying(8) COLLATE pg_catalog."default" NOT NULL,
    pass character varying(255) COLLATE pg_catalog."default" NOT NULL,
    token character varying(512) COLLATE pg_catalog."default",
    id_persona integer,
    CONSTRAINT usuarios_pkey PRIMARY KEY (id),
    CONSTRAINT usuarios_dni_key UNIQUE (dni),
    CONSTRAINT fk_persona FOREIGN KEY (id_persona)
        REFERENCES public.personas (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.usuarios
    OWNER to avnadmin;

-- Tabla de permisos
CREATE TABLE IF NOT EXISTS public.permisos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT
);

-- Relación entre roles y permisos
CREATE TABLE IF NOT EXISTS public.roles_permisos (
    rol_id INTEGER NOT NULL,
    permiso_id INTEGER NOT NULL,
    FOREIGN KEY (rol_id) REFERENCES public.roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permiso_id) REFERENCES public.permisos(id) ON DELETE CASCADE,
    PRIMARY KEY (rol_id, permiso_id)
);

CREATE TABLE IF NOT EXISTS public.usuarios_permisos (
    id_usuario INTEGER NOT NULL,
    id_permiso INTEGER NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (id_permiso) REFERENCES public.permisos(id) ON DELETE CASCADE,
    PRIMARY KEY (id_usuario, id_permiso)
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

-----------------------------------------------------------------------

-- Trigger para la tabla ventas_contables
CREATE OR REPLACE FUNCTION insertar_movimiento_venta()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO movimientos (
        movimiento_id,
        fecha,
        tipo_comprobante,
        serie_comprobante,
        numero_comprobante,
        tipo_documento,
        numero_documento,
        entidad,
        tipo_movimiento,
        sub_sin_igv,
        igv,
        total
    )
    VALUES (
        'V-' || NEW.id,  -- Generar un ID único combinando un prefijo con el ID de la venta
        NEW.fecha,
        NEW.tipo_comprobante,
        NEW.serie_comprobante,
        NEW.numero_comprobante,
        NEW.tipo_documento,
        NEW.numero_documento,
        NEW.usuario,         -- Usuario como entidad en ventas
        'Ventas',
        NEW.sub_sin_igv,
        NEW.igv,
        NEW.total
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_insertar_movimiento_venta
AFTER INSERT ON ventas_contables
FOR EACH ROW
EXECUTE FUNCTION insertar_movimiento_venta();


-- Trigger para la tabla compras_contables
CREATE OR REPLACE FUNCTION insertar_movimiento_compra()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO movimientos (
        movimiento_id,
        fecha,
        tipo_comprobante,
        serie_comprobante,
        numero_comprobante,
        tipo_documento,
        numero_documento,
        entidad,
        tipo_movimiento,
        sub_sin_igv,
        igv,
        total
    )
    VALUES (
        'C-' || NEW.id,  -- Generar un ID único combinando un prefijo con el ID de la compra
        NEW.fecha,
        NEW.tipo_comprobante,
        NEW.serie_comprobante,
        NEW.numero_comprobante,
        NEW.tipo_documento,
        NEW.numero_documento,
        NEW.nombre_proveedor,  -- Nombre del proveedor como entidad en compras
        'Compras',
        NEW.sub_sin_igv,
        NEW.igv,
        NEW.total
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_insertar_movimiento_compra
AFTER INSERT ON compras_contables
FOR EACH ROW
EXECUTE FUNCTION insertar_movimiento_compra();
-------------------------------------------------------------------------
--LIBRO DIARIO:
SELECT
    DENSE_RANK() OVER (ORDER BY ac.numero_asiento) AS numero_correlativo,
    ac.fecha,
    CASE
        WHEN m.tipo_movimiento = 'Ventas' THEN 'Por la venta de mercadería'
        WHEN m.tipo_movimiento = 'Compras' THEN 'Por la compra de insumos'
        ELSE ''
    END AS glosa,
    CASE
        WHEN m.tipo_movimiento = 'Compras' THEN 8
        WHEN m.tipo_movimiento = 'Ventas' THEN 14
        ELSE NULL
    END AS codigo_del_libro,
    DENSE_RANK() OVER (ORDER BY ac.numero_asiento) AS numero_correlativo_documento,
    ac.numero_documento AS numero_documento_sustentatorio,
    ac.codigo_cuenta,
    ac.denominacion,
    ac.debe,
    ac.haber
FROM asientos_contables ac
JOIN movimientos m ON ac.numero_asiento = m.movimiento_id
ORDER BY numero_correlativo, ac.id;

--------------------------------------------------

SELECT
    DENSE_RANK() OVER (ORDER BY ac.numero_asiento) AS numero_correlativo,
    ac.fecha,
    CASE
        WHEN m.tipo_movimiento = 'Ventas' THEN 'Por la venta de mercadería'
        WHEN m.tipo_movimiento = 'Compras' THEN 'Por la compra de insumos'
        ELSE ''
    END AS glosa,
    CASE
        WHEN m.tipo_movimiento = 'Compras' THEN 8
        WHEN m.tipo_movimiento = 'Ventas' THEN 14
        ELSE NULL
    END AS codigo_del_libro,
    DENSE_RANK() OVER (ORDER BY ac.numero_asiento) AS numero_correlativo_documento,
    ac.numero_documento AS numero_documento_sustentatorio,
    ac.codigo_cuenta,
    ac.denominacion,
    ac.debe,
    ac.haber
FROM asientos_contables ac
JOIN movimientos m ON ac.numero_asiento = m.movimiento_id
WHERE EXTRACT(MONTH FROM ac.fecha) = %s
  AND EXTRACT(YEAR FROM ac.fecha) = %s
  AND (ac.debe IS NOT NULL AND ac.debe != 0 OR ac.haber IS NOT NULL AND ac.haber != 0)
ORDER BY numero_correlativo, ac.id;

----------------------------------------------

SELECT DISTINCT ac.codigo_cuenta
FROM asientos_contables ac
JOIN movimientos m ON ac.numero_asiento = m.movimiento_id
WHERE EXTRACT(MONTH FROM ac.fecha) = %s
  AND EXTRACT(YEAR FROM ac.fecha) = %s
  AND (ac.debe IS NOT NULL AND ac.debe != 0 OR ac.haber IS NOT NULL AND ac.haber != 0)
ORDER BY ac.codigo_cuenta;
