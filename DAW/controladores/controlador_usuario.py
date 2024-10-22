from database.bd_goldenstore import obtener_conexion
from datetime import datetime
import hashlib

def encriptar_contraseña(contraseña):
    sha256 = hashlib.sha256()
    sha256.update(contraseña.encode('utf-8'))
    return sha256.hexdigest()

def insertar_usuario(nombre, email, telefono, apellido, nombre_usuario, contrasenia, fecha_nacimiento, tipo_usuario):
    contrasenia_hash = encriptar_contraseña(contrasenia)
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("INSERT INTO usuarios(nombre, email, telefono, apellido, nombre_usuario, contrasena, fecha_nacimiento, tipo_usuario_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                       (nombre, email, telefono, apellido, nombre_usuario, contrasenia_hash, fecha_nacimiento, tipo_usuario))
        conexion.commit()
        ultimo = cursor.lastrowid
    conexion.close()
    return ultimo

def actualizar_token_usuario(usuario, token):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE usuarios SET token = %s WHERE email = %s", (token, usuario))
    conexion.commit()
    conexion.close()

def obtener_usuarios():
    conexion = obtener_conexion()
    usuarios = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id_usuario, nombre, email, telefono, apellido, nombre_usuario, contrasena, fecha_nacimiento, tipo_usuario_id FROM usuarios")
        usuarios = cursor.fetchall()
    conexion.close()
    return usuarios

def eliminar_usuario(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id,))
        filas_afectadas = cursor.rowcount
    conexion.commit()
    conexion.close()
    return filas_afectadas > 0

def obtener_usuario_por_id(id):
    conexion = obtener_conexion()
    usuario = None
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id_usuario, nombre, email, telefono, apellido, nombre_usuario, contrasena, fecha_nacimiento, tipo_usuario_id FROM usuarios WHERE id_usuario = %s", (id,))
        usuario = cursor.fetchone()
    conexion.close()
    return usuario

def obtener_usuario_por_nombre_usuario(username):
    conexion = obtener_conexion()
    usuario = None
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id_usuario, nombre, email, telefono, apellido, nombre_usuario, contrasena, fecha_nacimiento, tipo_usuario_id FROM usuarios WHERE nombre_usuario = %s", (username,))
            usuario = cursor.fetchone()
    except Exception as e:
        print(f"Error durante la consulta: {e}")
    finally:
        conexion.close()
    return usuario

def actualizar_usuario(nombre, email, telefono, apellido, nombre_usuario, contrasenia, fecha_nacimiento, tipo_usuario, id):
    contrasenia_hash = encriptar_contraseña(contrasenia)
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE usuarios SET nombre = %s, email = %s, telefono = %s, apellido = %s, nombre_usuario = %s, contrasena = %s, fecha_nacimiento = %s, tipo_usuario_id = %s WHERE id_usuario = %s",
                       (nombre, email, telefono, apellido, nombre_usuario, contrasenia_hash, fecha_nacimiento, tipo_usuario, id))
    conexion.commit()
    conexion.close()

def actualizar_usuario_por_usuario(nombre, apellido, email, telefono, fecha_nacimiento, id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE usuarios SET nombre = %s, apellido = %s, email = %s, telefono = %s, fecha_nacimiento = %s WHERE id_usuario = %s",
                       (nombre, apellido, email, telefono, fecha_nacimiento, id))
    conexion.commit()
    conexion.close()

def obtener_nombre_tipo_usuario():
    conexion = obtener_conexion()
    tipos_usuario = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id_tipo_usuario, nombre FROM tipos_usuario")
        tipos_usuario = cursor.fetchall()
    conexion.close()
    return tipos_usuario

def login(usuario, contrasenia):
    contrasenia_hash = encriptar_contraseña(contrasenia)
    conexion = obtener_conexion()
    usuarios = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT tipo_usuario_id, id_usuario, nombre, token, email FROM usuarios WHERE email = %s AND contrasena = %s", (usuario, contrasenia_hash))
            usuarios = cursor.fetchall()
    except Exception as e:
        print(f"Error durante el login: {e}")
    finally:
        conexion.close()
    return usuarios

def ver_pedidos_pendientes(id):
    conexion = obtener_conexion()
    estados = []
    with conexion.cursor() as cursor:
        cursor.execute("SET lc_time_names = 'es_ES';")
        cursor.execute("SELECT id_pedido, fecha_creacion, total FROM pedidos WHERE id_usuario = %s AND estado = 'pendiente'", (id,))
        estados = cursor.fetchall()
    conexion.close()
    return estados

def ver_tarjetas(id_usuario):
    conexion = obtener_conexion()
    tarjetas = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id_tarjeta, numero_tarjeta, titular, fecha_vencimiento, cvv FROM tarjetas WHERE id_usuario = %s AND activo = TRUE", (id_usuario,))
        tarjetas = cursor.fetchall()
    tarjetas_formateadas = []
    for tarjeta in tarjetas:
        fecha_vencimiento = tarjeta[3]
        fecha_vencimiento_formateada = datetime.strptime(str(fecha_vencimiento), '%Y-%m-%d').strftime('%Y/%m')
        tarjeta_formateada = (
            tarjeta[0],
            tarjeta[1],
            tarjeta[2],
            fecha_vencimiento_formateada,
            tarjeta[4]
        )
        tarjetas_formateadas.append(tarjeta_formateada)
    conexion.close()
    return tarjetas_formateadas

def agregar_tarjeta(numero_tarjeta, titular, fecha_vencimiento, cvv, id_usuario):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("INSERT INTO tarjetas(numero_tarjeta, titular, fecha_vencimiento, cvv, id_usuario) VALUES (%s, %s, %s, %s, %s)",
                       (numero_tarjeta, titular, fecha_vencimiento, cvv, id_usuario))
        ultimo = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return ultimo

def pago_pedido(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id_pedido, fecha_creacion, total FROM pedidos WHERE id_pedido = %s", (id,))
        return cursor.fetchone()
    conexion.close()

def detalle_pedido(id):
    conexion = obtener_conexion()
    detalles = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT p.nombre_producto, p.genero, dp.cantidad, p.precio, dp.cantidad * p.precio AS precio_sub, p.imagen
            FROM detalles_pedido dp
            JOIN productos p ON dp.id_producto = p.id_producto
            WHERE dp.id_pedido = %s
        """, (id,))
        detalles = cursor.fetchall()
    conexion.close()
    return detalles

def insertar_pago(id_pedido, id_tarjeta, total_pago):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("INSERT INTO pagos(id_pedido, id_tarjeta, total) VALUES (%s, %s, %s)", 
                       (id_pedido, id_tarjeta, total_pago))
        cursor.execute("UPDATE pedidos SET estado = 'pagado' WHERE id_pedido = %s", (id_pedido,))
        cursor.execute("""
            SELECT COALESCE(MAX(CAST(numero_comprobante AS UNSIGNED)), 0) 
            FROM comprobante_pago 
            WHERE serie_comprobante = 'B001' AND tipo_comprobante = 'Boleta'
        """)
        last_numero = cursor.fetchone()[0]
        next_numero = last_numero + 1
        numero_comprobante = str(next_numero).zfill(7)
        cursor.execute("""
            INSERT INTO comprobante_pago(id_pedido, tipo_comprobante, serie_comprobante, numero_comprobante) 
            VALUES (%s, 'Boleta', 'B001', %s)
        """, (id_pedido, numero_comprobante))
    conexion.commit()
    conexion.close()

def historial_pedido(id_usuario):
    conexion = obtener_conexion()
    historial = []
    with conexion.cursor() as cursor:
        cursor.execute("SET lc_time_names = 'es_ES';")
        cursor.execute("SELECT * FROM pedidos WHERE id_usuario = %s AND estado = 'pagado'", (id_usuario,))
        historial = cursor.fetchall()
    conexion.close()
    return historial

def historial_detalle_pedido(id_pedido):
    conexion = obtener_conexion()
    detalles = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT p.imagen, p.nombre_producto, p.precio, p.talla, p.genero, dp.cantidad, p.precio * dp.cantidad AS sub_total
            FROM pedidos pe
            JOIN detalles_pedido dp ON pe.id_pedido = dp.id_pedido
            JOIN productos p ON p.id_producto = dp.id_producto
            WHERE pe.id_pedido = %s
        """, (id_pedido,))
        detalles = cursor.fetchall()
    conexion.close()
    return detalles

def obtener_usuario_por_id_auth(id_usuario):
    conexion = obtener_conexion()
    usuario = None
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id_usuario, nombre_usuario, contrasena FROM usuarios WHERE id_usuario = %s", (id_usuario,))
            usuario = cursor.fetchone()
    except Exception as e:
        print(f"Error durante la consulta: {e}")
    finally:
        conexion.close()
    return usuario

def obtener_user_por_username(nombre_usuario):
    conexion = obtener_conexion()
    usuario = None
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id_usuario, nombre_usuario, contrasena FROM usuarios WHERE nombre_usuario = %s", (nombre_usuario,))
            usuario = cursor.fetchone()
    except Exception as e:
        print(f"Error durante la consulta: {e}")
    finally:
        conexion.close()
    return usuario

def obtener_nombre_tipo_usuario_x_id(id_tipo_usuario):
    conexion = obtener_conexion()
    tipos_usuario = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id_tipo_usuario, nombre FROM tipos_usuario WHERE id_tipo_usuario = %s", (id_tipo_usuario,))
        tipos_usuario = cursor.fetchall()
    conexion.close()
    return tipos_usuario

def insertar_tipo_usuario(nombre):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("INSERT INTO tipos_usuario(nombre) VALUES (%s)", (nombre,))
        ultimo_id = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return ultimo_id

def actualizar_tipo_usuario(nombre, id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE tipos_usuario SET nombre = %s WHERE id_tipo_usuario = %s", (nombre, id))
        filas_afectadas = cursor.rowcount
    conexion.commit()
    conexion.close()
    return filas_afectadas > 0

def eliminar_tipo_usuario(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("DELETE FROM tipos_usuario WHERE id_tipo_usuario = %s", (id,))
        filas_afectadas = cursor.rowcount
    conexion.commit()
    conexion.close()
    return filas_afectadas > 0

def obtener_tarjetas():
    conexion = obtener_conexion()
    tarjetas = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id_tarjeta, numero_tarjeta, titular, fecha_vencimiento, cvv, id_usuario FROM tarjetas")
        tarjetas = cursor.fetchall()
    conexion.close()
    return tarjetas

def actualizar_tarjeta(numero_tarjeta, titular, fecha_vencimiento, cvv, id_usuario, id_tarjeta):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE tarjetas SET numero_tarjeta = %s, titular = %s, fecha_vencimiento = %s, cvv = %s, id_usuario = %s WHERE id_tarjeta = %s",
                       (numero_tarjeta, titular, fecha_vencimiento, cvv, id_usuario, id_tarjeta))
        filas_afectadas = cursor.rowcount
    conexion.commit()
    conexion.close()
    return filas_afectadas > 0

def dar_de_baja_tarjeta(id_tarjeta):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE tarjetas SET activo = FALSE WHERE id_tarjeta = %s", (id_tarjeta,))
        filas_afectadas = cursor.rowcount
    conexion.commit()
    conexion.close()
    return filas_afectadas > 0

def contador_usuarios():
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS con FROM usuarios")
        result = cursor.fetchone()
        return {'con': result[0]}
    conexion.close()

def contador_productos():
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS con FROM productos")
        result = cursor.fetchone()
        return {'con': result[0]}
    conexion.close()

def contador_productos_sin_stock():
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS con FROM productos WHERE stock <= 0")
        result = cursor.fetchone()
        return {'con': result[0]}
    conexion.close()

def obtener_direccion():
    conexion = obtener_conexion()
    direcciones = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id_direccion, pais, departamento, ciudad, direccion_1, direccion_2, id_usuario FROM direcciones")
        direcciones = cursor.fetchall()
    conexion.close()
    return direcciones

def obtener_direccion_por_id(id):
    conexion = obtener_conexion()
    direcciones = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id_direccion, pais, departamento, ciudad, direccion_1, direccion_2, id_usuario FROM direcciones WHERE id_direccion = %s", (id,))
        direcciones = cursor.fetchall()
    conexion.close()
    return direcciones

def insertar_direccion(pais, departamento, ciudad, direccion1, direccion2, usuarios_id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("INSERT INTO direcciones(pais, departamento, ciudad, direccion_1, direccion_2, id_usuario) VALUES (%s, %s, %s, %s, %s, %s)",
                       (pais, departamento, ciudad, direccion1, direccion2, usuarios_id))
        ultimo = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return ultimo

def actualizar_direccion(pais, departamento, ciudad, direccion1, direccion2, usuarios_id, id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE direcciones SET pais= %s, departamento = %s, ciudad= %s, direccion_1= %s, direccion_2= %s, id_usuario= %s WHERE id_direccion = %s",
                       (pais, departamento, ciudad, direccion1, direccion2, usuarios_id, id))
    conexion.commit()
    conexion.close()

def eliminar_direccion(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("DELETE FROM direcciones WHERE id_direccion = %s", (id,))
    conexion.commit()
    conexion.close()

def api_pago():
    conexion = obtener_conexion()
    pagos = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id_pago, id_pedido, id_tarjeta, fecha_pago, total FROM pagos")
        pagos = cursor.fetchall()
    conexion.close()
    return pagos

def api_pago_por_id(id):
    conexion = obtener_conexion()
    pagos = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id_pago, id_pedido, id_tarjeta, fecha_pago, total FROM pagos WHERE id_pago = %s", (id,))
        pagos = cursor.fetchall()
    conexion.close()
    return pagos

def insertar_pago_return(pedido_id, tarjeta_id, total_pago):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.callproc("realizar_pago", (pedido_id, tarjeta_id, total_pago))
        cursor.execute("SELECT COUNT(*) + 1 FROM pagos")
        ultimo = cursor.fetchone()[0]
    conexion.commit()
    conexion.close()
    return ultimo

def actualizar_pago(fecha_pago, total, pedido_id, tarjeta_id, id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(
            "UPDATE pagos SET fecha_pago = %s, total = %s, id_pedido = %s, id_tarjeta = %s, estado = 'completado' WHERE id_pago = %s",
            (fecha_pago, total, pedido_id, tarjeta_id, id)
        )
    conexion.commit()
    conexion.close()

def eliminar_pago(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("DELETE FROM pagos WHERE id_pago = %s", (id,))
    conexion.commit()
    conexion.close()

def cancelar_pedido(id_pedido):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id_producto, cantidad FROM detalles_pedido WHERE id_pedido = %s", (id_pedido,))
            detalles = cursor.fetchall()
            for detalle in detalles:
                id_producto, cantidad = detalle
                cursor.execute("UPDATE productos SET stock = stock + %s WHERE id_producto = %s", (cantidad, id_producto))
            cursor.execute("UPDATE pedidos SET estado = 'cancelado' WHERE id_pedido = %s", (id_pedido,))
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        raise e
    finally:
        conexion.close()

def contador_usuarios():
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as con FROM usuarios")
        result = cursor.fetchone()
        return {'con': result[0]}
    conexion.close()

def contador_productos():
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as con FROM productos")
        result = cursor.fetchone()
        return {'con': result[0]}
    conexion.close()

def contador_producto_sin_stock():
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS con FROM productos WHERE stock <= 0")
        result = cursor.fetchone()
        return {'con': result[0]}
    conexion.close()

def contador_pedidos():
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as con FROM pedidos")
        result = cursor.fetchone()
        return {'con': result[0]}
    conexion.close()

def contador_pedidos_pendientes():
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as con FROM pedidos_pendiente")
        result = cursor.fetchone()
        return {'con': result[0]}
    conexion.close()

def contador_pedidos_enviados():
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as con FROM pedidos_enviados")
        result = cursor.fetchone()
        return {'con': result[0]}
    conexion.close()

def contador_pagos():
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as con FROM pagos")
        result = cursor.fetchone()
        return {'con': result[0]}
    conexion.close()

def obtener_mantenimiento_tarjeta():
    conexion = obtener_conexion()
    tarjetas = []
    with conexion.cursor() as cursor:
        cursor.execute("""
                       SELECT tar.id_tarjeta, usu.nombre, tar.numero_tarjeta, tar.titular,
                            tar.fecha_vencimiento, tar.cvv
                            FROM tarjetas tar
                            JOIN usuarios usu ON tar.id_usuario = usu.id_usuario
                        """)
        tarjetas = cursor.fetchall()
    conexion.close()
    return tarjetas

def obtener_mantenimiento_tarjeta_x_id(id):
    conexion = obtener_conexion()
    tarjeta = []
    with conexion.cursor() as cursor:
        cursor.execute("""
                       SELECT tar.id_tarjeta, usu.nombre, tar.numero_tarjeta, tar.titular,
                            tar.fecha_vencimiento, tar.cvv, usu.id_usuario
                            FROM tarjetas tar
                            JOIN usuarios usu ON tar.id_usuario = usu.id_usuario
                            WHERE tar.id_tarjeta = %s
                        """, (id,))
        tarjeta = cursor.fetchone()
    conexion.close()
    return tarjeta

def obtener_direccion_mantenimiento():
    conexion = obtener_conexion()
    direcciones = []
    with conexion.cursor() as cursor:
        cursor.execute("""
                       SELECT usu.nombre, dir.id_direccion, dir.pais, dir.departamento, dir.ciudad, 
                            dir.direccion_1, dir.direccion_2 
                            FROM direcciones dir
                            JOIN usuarios usu ON dir.id_usuario = usu.id_usuario
                        """)
        direcciones = cursor.fetchall()
    conexion.close()
    return direcciones

def obtener_direccion_id_mantenimiento(id):
    conexion = obtener_conexion()
    direccion = []
    with conexion.cursor() as cursor:
        cursor.execute("""
                       SELECT usu.id_usuario, usu.nombre, dir.id_direccion, dir.pais, dir.departamento, dir.ciudad, 
                            dir.direccion_1, dir.direccion_2 
                            FROM direcciones dir
                            JOIN usuarios usu ON dir.id_usuario = usu.id_usuario
                            WHERE dir.id_direccion = %s
                       """, (id,))
        direccion = cursor.fetchone()
    conexion.close()
    return direccion

def obtener_nombre_tipo_usuario_x_id(id):
    conexion = obtener_conexion()
    tipo_usuario = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id_tipo_usuario, nombre FROM tipos_usuario WHERE id_tipo_usuario = %s", (id,))
        tipo_usuario = cursor.fetchone()
    conexion.close()
    return tipo_usuario

def ver_pedidos_general_enviados():
    conexion = obtener_conexion()
    estados = []
    with conexion.cursor() as cursor:
        cursor.execute("SET lc_time_names = 'es_ES';")
        cursor.execute("""
                       SELECT usu.nombre, usu.email ,pe.* FROM pedidos_enviados pe
                        JOIN usuarios usu ON pe.id_usuario = usu.id
                       """)
        estados = cursor.fetchall()
    conexion.close()
    return estados

def ver_pedidos_general_PENDIENTE():
    conexion = obtener_conexion()
    estados = []
    with conexion.cursor() as cursor:
        cursor.execute("SET lc_time_names = 'es_ES';")
        cursor.execute("""
                       SELECT usu.nombre, usu.email,pe.* FROM pedidos_pendiente pe
                        JOIN usuarios usu ON pe.id_usuario = usu.id
                       """)
        estados = cursor.fetchall()
    conexion.close()
    return estados

def obtener_compras():
    conexion = obtener_conexion()
    compras = []
    with conexion.cursor() as cursor:
        query = """
            SELECT c.id_compra, p.nombre_proveedor, c.fecha_compra, c.total, c.estado
            FROM compras c
            JOIN proveedores p ON c.id_proveedor = p.id_proveedor
            ORDER BY c.fecha_compra DESC
        """
        cursor.execute(query)
        compras = cursor.fetchall()
    conexion.close()
    return compras

def obtener_compra_por_id(id_compra):
    conexion = obtener_conexion()
    compra = None
    detalles = []
    with conexion.cursor() as cursor:
        # Obtener la información de la compra
        query_compra = """
            SELECT c.id_compra, c.id_proveedor, c.fecha_compra, c.total, c.estado, p.nombre_proveedor
            FROM compras c
            JOIN proveedores p ON c.id_proveedor = p.id_proveedor
            WHERE c.id_compra = %s
        """
        cursor.execute(query_compra, (id_compra,))
        compra = cursor.fetchone()
        
        # Obtener los detalles de la compra
        query_detalles = """
            SELECT dc.id_detalle_compra, dc.id_producto, pr.nombre_producto, dc.cantidad, dc.subtotal
            FROM detalles_compra dc
            JOIN productos pr ON dc.id_producto = pr.id_producto
            WHERE dc.id_compra = %s
        """
        cursor.execute(query_detalles, (id_compra,))
        detalles = cursor.fetchall()
        
    conexion.close()
    return compra, detalles

def obtener_proveedores():
    conexion = obtener_conexion()
    proveedores = []
    with conexion.cursor() as cursor:
        query = "SELECT * FROM proveedores;"
        cursor.execute(query)
        proveedores = cursor.fetchall()
    conexion.close()
    return proveedores

def guardar_compra(datos_compra):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Insertar la compra
            query_compra = """
                INSERT INTO compras (id_proveedor, fecha_compra, total, estado)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query_compra, (
                datos_compra['id_proveedor'],
                datos_compra['fecha_compra'],
                datos_compra['total'],
                datos_compra['estado']
            ))
            id_compra = cursor.lastrowid
            
            # Insertar los detalles de la compra
            for detalle in datos_compra['detalles']:
                query_detalle = """
                    INSERT INTO detalles_compra (id_compra, id_producto, cantidad, subtotal)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query_detalle, (
                    id_compra,
                    detalle['id_producto'],
                    detalle['cantidad'],
                    detalle['subtotal']
                ))
                
                # Actualizar el stock del producto
                query_stock = """
                    UPDATE productos
                    SET stock = stock + %s
                    WHERE id_producto = %s
                """
                cursor.execute(query_stock, (
                    detalle['cantidad'],
                    detalle['id_producto']
                ))
                
            conexion.commit()
        return True
    except Exception as e:
        print(f"Error al guardar la compra: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()

def actualizar_compra(id_compra, datos_compra):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Actualizar la compra
            query_compra = """
                UPDATE compras
                SET id_proveedor = %s, fecha_compra = %s, total = %s, estado = %s
                WHERE id_compra = %s
            """
            cursor.execute(query_compra, (
                datos_compra['id_proveedor'],
                datos_compra['fecha_compra'],
                datos_compra['total'],
                datos_compra['estado'],
                id_compra
            ))
            
            # Eliminar los detalles existentes
            query_eliminar_detalles = "DELETE FROM detalles_compra WHERE id_compra = %s"
            cursor.execute(query_eliminar_detalles, (id_compra,))
            
            # Insertar los nuevos detalles
            for detalle in datos_compra['detalles']:
                query_detalle = """
                    INSERT INTO detalles_compra (id_compra, id_producto, cantidad, subtotal)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query_detalle, (
                    id_compra,
                    detalle['id_producto'],
                    detalle['cantidad'],
                    detalle['subtotal']
                ))
                
                # Actualizar el stock del producto
                query_stock = """
                    UPDATE productos
                    SET stock = stock + %s
                    WHERE id_producto = %s
                """
                cursor.execute(query_stock, (
                    detalle['cantidad'],
                    detalle['id_producto']
                ))
                
            conexion.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar la compra: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()

def eliminar_compra(id_compra):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Obtener los detalles de la compra para ajustar el stock
            query_detalles = "SELECT id_producto, cantidad FROM detalles_compra WHERE id_compra = %s"
            cursor.execute(query_detalles, (id_compra,))
            detalles = cursor.fetchall()
            
            # Revertir el stock de los productos
            for detalle in detalles:
                query_stock = """
                    UPDATE productos
                    SET stock = stock - %s
                    WHERE id_producto = %s
                """
                cursor.execute(query_stock, (
                    detalle['cantidad'],
                    detalle['id_producto']
                ))
            
            # Eliminar los detalles de la compra
            query_eliminar_detalles = "DELETE FROM detalles_compra WHERE id_compra = %s"
            cursor.execute(query_eliminar_detalles, (id_compra,))
            
            # Eliminar la compra
            query_eliminar_compra = "DELETE FROM compras WHERE id_compra = %s"
            cursor.execute(query_eliminar_compra, (id_compra,))
            
            conexion.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar la compra: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()