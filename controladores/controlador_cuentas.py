from bd_conexion import obtener_conexion

def obtener_todas_cuentas():
    conexion = obtener_conexion()
    cuentas = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            WITH cuenta_jerarquia AS (
                -- Seleccionamos todas las cuentas, verificamos si tienen subcuentas, y añadimos estado y categoría
                SELECT 
                    c1.cuenta_id AS id_cuenta,
                    c1.codigo AS codigo_cuenta,
                    c1.descripcion AS descripcion_cuenta,
                    c1.cuenta_padre AS cuenta_padre,
                    c1.estado AS estado_cuenta, -- Añadimos el estado de la cuenta
                    c1.categoria AS categoria_cuenta, -- Añadimos la categoría de la cuenta
                    CASE 
                        WHEN EXISTS (SELECT 1 FROM cuentas c2 WHERE c2.cuenta_padre = c1.cuenta_id)
                        THEN TRUE
                        ELSE FALSE
                    END AS tiene_subcuentas
                FROM cuentas c1
            )
            SELECT 
                id_cuenta,
                codigo_cuenta,
                descripcion_cuenta,
                cuenta_padre,
                estado_cuenta, -- Mostramos el estado de la cuenta
                categoria_cuenta, -- Mostramos la categoría de la cuenta
                tiene_subcuentas
            FROM cuenta_jerarquia
            ORDER BY id_cuenta;
        """)
        cuentas = cursor.fetchall()
    conexion.close()
    return cuentas
