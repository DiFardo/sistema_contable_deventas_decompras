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

CREATE OR REPLACE FUNCTION public.registrar_asiento_movimiento()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
DECLARE
    base_imponible NUMERIC;
    igv NUMERIC;
    total_comprobante NUMERIC;
    numero_documento VARCHAR(255);
    -- Variables para códigos y descripciones
    codigo_cuenta_cobrar VARCHAR(10);
    descripcion_cuenta_cobrar VARCHAR(255);
    codigo_cuenta_ventas VARCHAR(10);
    descripcion_cuenta_ventas VARCHAR(255);
    codigo_cuenta_igv VARCHAR(10);
    descripcion_cuenta_igv VARCHAR(255);
    codigo_cuenta_costo_ventas VARCHAR(10);
    descripcion_cuenta_costo_ventas VARCHAR(255);
    codigo_cuenta_mercaderias VARCHAR(10);
    descripcion_cuenta_mercaderias VARCHAR(255);
    -- Variables para cuentas de compras
    codigo_cuenta_compras VARCHAR(10);
    descripcion_cuenta_compras VARCHAR(255);
    codigo_cuenta_materias_primas VARCHAR(10);
    descripcion_cuenta_materias_primas VARCHAR(255);
    codigo_cuenta_pagar VARCHAR(10);
    descripcion_cuenta_pagar VARCHAR(255);
    codigo_cuenta_costo_mp VARCHAR(10);
    descripcion_cuenta_costo_mp VARCHAR(255);
    codigo_cuenta_variacion_inv VARCHAR(10);
    descripcion_cuenta_variacion_inv VARCHAR(255);
    codigo_cuenta_variacion_inv_mp VARCHAR(10);
    descripcion_cuenta_variacion_inv_mp VARCHAR(255);
BEGIN
    -- Definir valores base
    base_imponible := NEW.sub_sin_igv;
    igv := NEW.igv;
    total_comprobante := base_imponible + igv;
    numero_documento := NEW.serie_comprobante || '-' || NEW.numero_comprobante;
    -- Obtener código y descripción de cada cuenta desde la tabla `cuentas`
    SELECT codigo INTO codigo_cuenta_cobrar FROM cuentas WHERE codigo = '10'; -- Efectivo y equivalentes de efectivo
    SELECT descripcion INTO descripcion_cuenta_cobrar FROM cuentas WHERE codigo = '10';
    SELECT codigo INTO codigo_cuenta_ventas FROM cuentas WHERE codigo = '70'; -- Ventas
    SELECT descripcion INTO descripcion_cuenta_ventas FROM cuentas WHERE codigo = '70';
    SELECT codigo INTO codigo_cuenta_igv FROM cuentas WHERE codigo = '40'; -- IGV
    SELECT descripcion INTO descripcion_cuenta_igv FROM cuentas WHERE codigo = '40';
    SELECT codigo INTO codigo_cuenta_costo_ventas FROM cuentas WHERE codigo = '69'; -- Costo de Ventas
    SELECT descripcion INTO descripcion_cuenta_costo_ventas FROM cuentas WHERE codigo = '69';
    SELECT codigo INTO codigo_cuenta_mercaderias FROM cuentas WHERE codigo = '20'; -- Mercaderías
    SELECT descripcion INTO descripcion_cuenta_mercaderias FROM cuentas WHERE codigo = '20';
    -- Cuentas de compras
    SELECT codigo INTO codigo_cuenta_compras FROM cuentas WHERE codigo = '60'; -- Compras
    SELECT descripcion INTO descripcion_cuenta_compras FROM cuentas WHERE codigo = '60';
    SELECT codigo INTO codigo_cuenta_materias_primas FROM cuentas WHERE codigo = '602'; -- Materias Primas
    SELECT descripcion INTO descripcion_cuenta_materias_primas FROM cuentas WHERE codigo = '602';
    SELECT codigo INTO codigo_cuenta_pagar FROM cuentas WHERE codigo = '10'; -- Efectivo y equivalentes de efectivo
    SELECT descripcion INTO descripcion_cuenta_pagar FROM cuentas WHERE codigo = '10';
    SELECT codigo INTO codigo_cuenta_costo_mp FROM cuentas WHERE codigo = '241'; -- Materias Primas - Costo
    SELECT descripcion INTO descripcion_cuenta_costo_mp FROM cuentas WHERE codigo = '241';
    SELECT codigo INTO codigo_cuenta_variacion_inv FROM cuentas WHERE codigo = '61'; -- Variación de Inventarios
    SELECT descripcion INTO descripcion_cuenta_variacion_inv FROM cuentas WHERE codigo = '61';
    SELECT codigo INTO codigo_cuenta_variacion_inv_mp FROM cuentas WHERE codigo = '612'; -- Variación de Inventarios - Materias Primas
    SELECT descripcion INTO descripcion_cuenta_variacion_inv_mp FROM cuentas WHERE codigo = '612';
    IF NEW.tipo_movimiento = 'Ventas' THEN
        -- Registro del asiento contable para ventas de productos terminados
        INSERT INTO asientos_contables (numero_asiento, fecha, codigo_cuenta, denominacion, debe, haber, numero_documento)
        VALUES 
            (NEW.movimiento_id, NEW.fecha, codigo_cuenta_cobrar, descripcion_cuenta_cobrar, NULL, NULL, numero_documento), -- Efectivo y Equivalentes de Efectivo
            (NEW.movimiento_id, NEW.fecha, '104', 'Cuentas corrientes en instituciones financieras', NULL, NULL, numero_documento),
            (NEW.movimiento_id, NEW.fecha, '1041', 'Cuentas corrientes operativas', total_comprobante, NULL, numero_documento),
            (NEW.movimiento_id, NEW.fecha, codigo_cuenta_igv, descripcion_cuenta_igv, NULL, NULL, numero_documento), -- Tributos y Aportes
            (NEW.movimiento_id, NEW.fecha, '401', 'Gobierno central', NULL, NULL, numero_documento),
            (NEW.movimiento_id, NEW.fecha, '4011', 'Impuesto general a las ventas', NULL, NULL, numero_documento),
            (NEW.movimiento_id, NEW.fecha, '40111', 'IGV – Cuenta propia', NULL, igv, numero_documento),
            (NEW.movimiento_id, NEW.fecha, codigo_cuenta_ventas, descripcion_cuenta_ventas, NULL, NULL, numero_documento), -- Ventas
            (NEW.movimiento_id, NEW.fecha, '701', 'Mercaderías', NULL, NULL, numero_documento),
            (NEW.movimiento_id, NEW.fecha, '7012', 'Mercaderías - Venta local', NULL, NULL, numero_documento),
            (NEW.movimiento_id, NEW.fecha, '70111', 'Terceros', NULL, base_imponible, numero_documento);
    ELSIF NEW.tipo_movimiento = 'Compras' THEN
        -- Registro del asiento contable para compras de materias primas
        INSERT INTO asientos_contables (numero_asiento, fecha, codigo_cuenta, denominacion, debe, haber, numero_documento)
        VALUES 
            (NEW.movimiento_id, NEW.fecha, codigo_cuenta_compras, descripcion_cuenta_compras, NULL, NULL, numero_documento), -- Compras
            (NEW.movimiento_id, NEW.fecha, codigo_cuenta_materias_primas, descripcion_cuenta_materias_primas, base_imponible, NULL, numero_documento),
            (NEW.movimiento_id, NEW.fecha, codigo_cuenta_igv, descripcion_cuenta_igv, NULL, NULL, numero_documento), -- IGV
            (NEW.movimiento_id, NEW.fecha, '401', 'Gobierno central', NULL, NULL, numero_documento),
            (NEW.movimiento_id, NEW.fecha, '4011', 'Impuesto general a las ventas', NULL, NULL, numero_documento),
            (NEW.movimiento_id, NEW.fecha, '40111', 'IGV – Cuenta propia', igv, NULL, numero_documento),
            (NEW.movimiento_id, NEW.fecha, codigo_cuenta_pagar, descripcion_cuenta_pagar, NULL, NULL, numero_documento), -- Efectivo y Equivalentes de Efectivo
            (NEW.movimiento_id, NEW.fecha, '104', 'Cuentas corrientes en instituciones financieras', NULL, NULL, numero_documento),
            (NEW.movimiento_id, NEW.fecha, '1041', 'Cuentas corrientes operativas', NULL, total_comprobante, numero_documento);
    END IF;
    RETURN NEW;
END;
$BODY$;