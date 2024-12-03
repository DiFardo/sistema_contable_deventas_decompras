--En la bd de contabilidad
CREATE TABLE ventas_contables (
    id SERIAL PRIMARY KEY,
    id_pedido INT NOT NULL,
    id_usuario INT NOT NULL,
	usuario VARCHAR(255) NOT NULL,
    tipo_documento VARCHAR(20) NOT NULL,
    numero_documento VARCHAR(30) NOT NULL,
    fecha TIMESTAMP NOT NULL,
    sub_sin_igv NUMERIC(10, 2) NOT NULL,
    igv NUMERIC(10, 2) NOT NULL,
    total NUMERIC(10, 2) NOT NULL,
    tipo_comprobante VARCHAR(20) NOT NULL,
    serie_comprobante VARCHAR(10) NOT NULL,
    numero_comprobante VARCHAR(10) NOT NULL
);

CREATE TABLE compras_contables (
    id SERIAL PRIMARY KEY,
    id_compra INT NOT NULL,
    id_usuario INT NOT NULL,
    usuario VARCHAR(255) NOT NULL,
    id_proveedor INT NOT NULL,
    nombre_proveedor VARCHAR(255) NOT NULL,
    tipo_documento VARCHAR(20) NOT NULL,
    numero_documento VARCHAR(30) NOT NULL,
    fecha TIMESTAMP NOT NULL,
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
    tipo_documento VARCHAR(20) NOT NULL, --DNI, RUC, Pasaporte, etc
    numero_documento VARCHAR(30) NOT NULL,
    entidad VARCHAR(255) NOT NULL, --Persona o empresa, ejemplo: "Gustavo Gil", o "HERMANOS SAC"
    tipo_movimiento VARCHAR(10) NOT NULL CHECK (tipo_movimiento IN ('Ventas', 'Compras')),
    sub_sin_igv NUMERIC(10, 2) NOT NULL,
    igv NUMERIC(10, 2) NOT NULL,
    total NUMERIC(10, 2) NOT NULL
);
/*
EJEMPLO DE movimientos:
"movimiento_id"	"fecha"	"tipo_comprobante"	"serie_comprobante"	"numero_comprobante"	"tipo_documento"	"numero_documento"	"entidad"	"tipo_movimiento"	"sub_sin_igv"	"igv"	"total"
"V-60"	"2024-10-13 10:41:47"	"Boleta"	"B001"	"0000001"	"DNI"	"71937486"	"Gustavo Gil"	"Ventas"	67.80	12.20	80.00
"C-32"	"2024-11-09 10:48:39"	"Factura"	"C002"	"0000008"	"RUC"	"20198765432"	"Decoraciones Elegantes"	"Compras"	6059.32	1090.68	7150.00
"V-68"	"2024-10-29 01:43:52"	"Factura"	"F001"	"0000001"	"RUC"	"10174131612"	"HERMANOS SAC"	"Ventas"	150.00	27.00	177.00
*/
CREATE TABLE asientos_contables (
    id SERIAL PRIMARY KEY,
    numero_asiento VARCHAR(20),
    fecha TIMESTAMP,
    codigo_cuenta VARCHAR(10),
    denominacion VARCHAR(255),
    debe NUMERIC,
    haber NUMERIC,
    numero_documento VARCHAR(255)
);
/*
EJEMPLO DE asientos_contables:
"id"	"numero_asiento"	"fecha"	"codigo_cuenta"	"denominacion"
837	"V-60"	"2024-10-13 10:41:47"	"40"	"TRIBUTOS, CONTRAPRESTACIONES Y APORTES AL SISTEMA PÚBLICO DE PENSIONES Y DE SALUD POR PAGAR"
838	"V-60"	"2024-10-13 10:41:47"	"401"	"Gobierno central"
839	"V-60"	"2024-10-13 10:41:47"	"4011"	"Impuesto general a las ventas"
840	"V-60"	"2024-10-13 10:41:47"	"40111"	"IGV – Cuenta propia"
841	"V-60"	"2024-10-13 10:41:47"	"70"	"VENTAS"
842	"V-60"	"2024-10-13 10:41:47"	"701"	"Mercaderías"
843	"V-60"	"2024-10-13 10:41:47"	"7012"	"Mercaderías - Venta local"
844	"V-60"	"2024-10-13 10:41:47"	"70111"	"Terceros"
834	"V-60"	"2024-10-13 10:41:47"	"10"	"EFECTIVO Y EQUIVALENTES DE EFECTIVO"
*/
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    estado BOOLEAN DEFAULT TRUE
);
/*
roles:
"id"	"nombre"	"descripcion"	"estado"
1	"Contador"	"Responsable de gestionar y analizar las finanzas de la empresa, asegurando su legalidad y precisión."	true
2	"Gestor de operaciones comerciales"	"Encargado de gestionar y analizar las transacciones de compras y ventas, asegurando su eficiencia y precisión."	true
3	"Administrador"	"Encargado de gestionar y analizar tanto las finanzas como las transacciones comerciales de la empresa."	true
*/
CREATE TABLE personas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    dni VARCHAR(8) NOT NULL UNIQUE,
    imagen VARCHAR(255),
    id_rol INTEGER,
    FOREIGN KEY (id_rol) REFERENCES roles(id) ON UPDATE CASCADE ON DELETE SET NULL
);
/*
EJEMPLO personas:
"id"	"nombre"	"apellido"	"dni"	"imagen"	"id_rol"
2	"Gustavo"	"Gil"	"71937486"	"Miyamura_Izumi_icons.jpeg"	3
*/
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    dni VARCHAR(8) NOT NULL UNIQUE,
    pass VARCHAR(255) NOT NULL,
    token VARCHAR(512),
    id_persona INTEGER,
    FOREIGN KEY (id_persona) REFERENCES public.personas(id) ON UPDATE NO ACTION ON DELETE NO ACTION
);
/*
EJEMPLO usuarios:
"id"	"dni"	"pass"	"token"	"id_persona"
2	"71937486"	"e70..."   "eyJhba..."    2
*/
CREATE TABLE permisos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT
);
/*
permisos:
"id"	"nombre"	"descripcion"
1	"ver_cuentas"	"Ver las cuentas contables"
2	"editar_cuentas"	"Editar las cuentas contables"
3	"darbaja_cuentas"	"Dar de baja las cuentas contables"
4	"agregar_cuentas"	"Agregar nuevas cuentas contables"
*/
CREATE TABLE roles_permisos (
    rol_id INTEGER NOT NULL,
    permiso_id INTEGER NOT NULL,
    FOREIGN KEY (rol_id) REFERENCES public.roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permiso_id) REFERENCES public.permisos(id) ON DELETE CASCADE,
    PRIMARY KEY (rol_id, permiso_id)
);
/*
roles_permisos:
"rol_id"	"permiso_id"
1	1
*/
CREATE TABLE usuarios_permisos (
    id_usuario INTEGER NOT NULL,
    id_permiso INTEGER NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (id_permiso) REFERENCES public.permisos(id) ON DELETE CASCADE,
    PRIMARY KEY (id_usuario, id_permiso)
);
/*
EJEMPLO usuarios_permisos:
"id_usuario"	"id_permiso"
22	4
*/
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
