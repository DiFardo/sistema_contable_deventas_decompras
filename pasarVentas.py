import mysql.connector
import psycopg2
import time

mysql_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'goldenstore'
}

mysql_connection = mysql.connector.connect(**mysql_config)
mysql_cursor = mysql_connection.cursor()

postgres_config = {
    'dbname': 'servidor_sistema_contable',
    'user': 'avnadmin',
    'password': 'AVNS_8q6hd4Rhe2XMjRIpU_G',
    'host': 'pg-servercontable-calidad-2024.d.aivencloud.com',
    'port': 26134
}

postgres_connection = psycopg2.connect(**postgres_config)
postgres_cursor = postgres_connection.cursor()

def verificar_pedidos():
    while True:
        mysql_cursor.execute("""
            SELECT 
                dp.id_detalle, 
                dp.id_pedido, 
                p.id_usuario,
                CASE 
                    WHEN u.apellido IS NOT NULL AND u.apellido != '' 
                        THEN CONCAT(u.nombre, ' ', u.apellido)
                    ELSE u.nombre
                END AS usuario,
                u.tipo_documento,
                u.numero_documento,
                pa.fecha_pago AS fecha, 
                dp.id_producto, 
                pr.nombre_producto, 
                dp.cantidad, 
                ROUND(dp.cantidad * pr.precio, 2) AS total_con_igv,
                ROUND((dp.cantidad * pr.precio) / 1.18, 2) AS sub_sin_igv,
                ROUND((dp.cantidad * pr.precio) - ((dp.cantidad * pr.precio) / 1.18), 2) AS igv,
                cp.tipo_comprobante,
                cp.serie_comprobante,
                cp.numero_comprobante
            FROM detalles_pedido dp
            JOIN pedidos p ON dp.id_pedido = p.id_pedido
            JOIN usuarios u ON p.id_usuario = u.id_usuario
            JOIN productos pr ON dp.id_producto = pr.id_producto
            JOIN pagos pa ON pa.id_pedido = p.id_pedido
            JOIN comprobante_pago cp ON cp.id_pedido = p.id_pedido  
            WHERE p.estado = 'pagado' AND p.registrado_en_contable = FALSE;
        """)
        resultados = mysql_cursor.fetchall()

        for detalle in resultados:
            registrar_en_contable(detalle)

        verificar_compras()
        time.sleep(60)

def registrar_en_contable(detalle):
    (id_detalle, id_pedido, id_usuario, usuario, tipo_documento, numero_documento, fecha, 
     id_producto, nombre_producto, cantidad, total_con_igv, sub_sin_igv, igv, 
     tipo_comprobante, serie_comprobante, numero_comprobante) = detalle

    try:
        postgres_cursor.execute("""
            INSERT INTO ventas_contables (
                id_detalle, id_pedido, id_usuario, usuario, tipo_documento, numero_documento, 
                fecha, id_producto, nombre_producto, cantidad, sub_sin_igv, igv, subtotal, 
                tipo_comprobante, serie_comprobante, numero_comprobante
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (id_detalle, id_pedido, id_usuario, usuario, tipo_documento, numero_documento, 
              fecha, id_producto, nombre_producto, cantidad, sub_sin_igv, igv, 
              total_con_igv, tipo_comprobante, serie_comprobante, numero_comprobante))
        postgres_connection.commit()

        print(f"Detalle de pedido {id_detalle} registrado en el sistema contable.")

        mysql_cursor.execute("""
            UPDATE pedidos SET registrado_en_contable = TRUE WHERE id_pedido = %s;
        """, (id_pedido,))
        mysql_connection.commit()

    except Exception as e:
        print(f"Error al registrar detalle de pedido {id_detalle}: {e}")
        postgres_connection.rollback()

def verificar_compras():
    mysql_cursor.execute("""
        SELECT 
            dc.id_detalle_compra,
            c.id_compra,
            c.id_usuario,
            CASE 
                WHEN u.apellido IS NOT NULL AND u.apellido != '' 
                    THEN CONCAT(u.nombre, ' ', u.apellido)
                ELSE u.nombre
            END AS usuario,
            c.id_proveedor,
            p.nombre_proveedor,
            p.tipo_documento,
            p.numero_documento,
            c.fecha_compra AS fecha,
            dc.id_insumo,
            im.nombre_insumo,
            dc.cantidad,
            ROUND(dc.cantidad * im.precio_unitario / 1.18, 2) AS sub_sin_igv,
            ROUND(dc.cantidad * im.precio_unitario - (dc.cantidad * im.precio_unitario / 1.18), 2) AS igv,
            ROUND(dc.cantidad * im.precio_unitario, 2) AS subtotal,
            c.tipo_comprobante,
            c.serie_comprobante,
            c.numero_comprobante
        FROM detalles_compra dc
        JOIN compras c ON dc.id_compra = c.id_compra
        JOIN usuarios u ON c.id_usuario = u.id_usuario
        JOIN proveedores p ON c.id_proveedor = p.id_proveedor
        JOIN insumos_materiales im ON dc.id_insumo = im.id_insumo
        WHERE c.estado = 'pagado' AND c.registrado_en_contable = FALSE;
    """)
    compras_resultados = mysql_cursor.fetchall()

    for detalle_compra in compras_resultados:
        registrar_compra_en_contable(detalle_compra)

def registrar_compra_en_contable(detalle_compra):
    (id_detalle_compra, id_compra, id_usuario, usuario, id_proveedor, nombre_proveedor, 
     tipo_documento, numero_documento, fecha, id_insumo, nombre_insumo, cantidad, 
     sub_sin_igv, igv, subtotal, tipo_comprobante, serie_comprobante, numero_comprobante) = detalle_compra

    try:
        postgres_cursor.execute("""
            INSERT INTO compras_contables (
                id_detalle_compra, id_compra, id_usuario, usuario, id_proveedor, nombre_proveedor, 
                tipo_documento, numero_documento, fecha, id_insumo, nombre_insumo, cantidad, 
                sub_sin_igv, igv, subtotal, tipo_comprobante, serie_comprobante, numero_comprobante
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (id_detalle_compra, id_compra, id_usuario, usuario, id_proveedor, nombre_proveedor, 
              tipo_documento, numero_documento, fecha, id_insumo, nombre_insumo, cantidad, 
              sub_sin_igv, igv, subtotal, tipo_comprobante, serie_comprobante, numero_comprobante))
        postgres_connection.commit()

        print(f"Detalle de compra {id_detalle_compra} registrado en el sistema contable.")

        mysql_cursor.execute("""
            UPDATE compras SET registrado_en_contable = TRUE WHERE id_compra = %s;
        """, (id_compra,))
        mysql_connection.commit()

    except Exception as e:
        print(f"Error al registrar detalle de compra {id_detalle_compra}: {e}")
        postgres_connection.rollback()

if __name__ == "__main__":
    verificar_pedidos()