from bd_conexion import obtener_conexion

def obtener_todas_ventas():
    conexion = obtener_conexion()
    ventas = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT 
                id, 
                id_detalle, 
                id_pedido, 
                id_usuario, 
                usuario, 
                fecha, 
                id_producto, 
                nombre_producto, 
                cantidad, 
                subtotal, 
                serie_comprobante, 
                numero_comprobante 
            FROM ventas_contables
            ORDER BY id;
        """)
        ventas = cursor.fetchall()
    conexion.close()
    return ventas

def obtener_boletas():
    conexion = obtener_conexion()
    boletas = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT 
                CONCAT(serie_comprobante, '-', numero_comprobante) AS Identificador,
                usuario AS Cliente,
                fecha AS "Fecha y Hora",
                SUM(subtotal) AS Total
            FROM 
                ventas_contables
            GROUP BY 
                serie_comprobante, 
                numero_comprobante, 
                usuario, 
                fecha
            ORDER BY 
                Identificador;
        """)
        boletas = cursor.fetchall()
    conexion.close()
    return boletas