from database.bd_goldenstore import obtener_conexion
from pymysql.cursors import DictCursor
from decimal import Decimal

def obtener_productos_mas_vendidos():
    conexion = obtener_conexion()
    productos_novedades = []
    with conexion.cursor(DictCursor) as cursor:
        query = """
        SELECT p.id_producto, p.nombre_producto, p.descripcion, p.precio, p.imagen, SUM(dp.cantidad) AS total_vendidos
        FROM productos p
        JOIN detalles_pedido dp ON p.id_producto = dp.id_producto
        JOIN pedidos pe ON dp.id_pedido = pe.id_pedido
        WHERE p.stock > 0
        GROUP BY p.id_producto
        ORDER BY total_vendidos DESC
        LIMIT 4;
        """
        cursor.execute(query)
        productos_novedades = cursor.fetchall()
    conexion.close()
    return productos_novedades

def insertar_producto(nombre, descripcion, precio, stock, id_categoria, ruta_imagen_db, talla, genero):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(
            "INSERT INTO productos (nombre_producto, descripcion, precio, stock, id_categoria, imagen, talla, genero) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (nombre, descripcion, precio, stock, id_categoria, ruta_imagen_db, talla, genero))
        ultimo = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return ultimo

def obtener_nombre_categoria():
    conexion = obtener_conexion()
    categorias = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id_categoria, nombre FROM categorias")
        categorias = cursor.fetchall()
    conexion.close()
    return categorias

def obtener_producto():
    conexion = obtener_conexion()
    productos = []
    with conexion.cursor() as cursor:
        cursor.execute("""
        SELECT p.id_producto, p.nombre_producto, p.descripcion, p.precio, p.stock,
        c.nombre AS nombre_categoria, p.imagen, p.fecha_creacion, p.talla, p.genero
        FROM productos p
        JOIN categorias c ON c.id_categoria = p.id_categoria;
        """)
        productos = cursor.fetchall()
    conexion.close()
    return productos

def eliminar_producto(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id,))
        filas_afectadas = cursor.rowcount
    conexion.commit()
    conexion.close()
    return filas_afectadas > 0

def obtener_producto_por_id(id):
    conexion = obtener_conexion()
    producto = None
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT id_producto, nombre_producto, descripcion, precio, stock, id_categoria, imagen, fecha_creacion, talla FROM productos WHERE id_producto = %s", (id,))
        producto = cursor.fetchone()
    conexion.close()
    return producto

def actualizar_producto(nombre, descripcion, precio, stock, id_categoria, imagen, talla, id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(
            "UPDATE productos SET nombre_producto = %s, descripcion = %s, precio = %s, stock = %s, id_categoria = %s, imagen = %s, talla = %s WHERE id_producto = %s",
            (nombre, descripcion, precio, stock, id_categoria, imagen, talla, id))
        filas_afectadas = cursor.rowcount
    conexion.commit()
    conexion.close()
    return filas_afectadas > 0

def obtener_productos():
    conexion = obtener_conexion()
    productos = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id_producto, nombre_producto, descripcion, precio, stock, id_categoria, imagen, fecha_creacion, talla FROM productos")
        productos = cursor.fetchall()
    conexion.close()
    return productos

def obtener_productos_hombre():
    conexion = obtener_conexion()
    productos = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id_producto, nombre_producto, descripcion, precio, stock, id_categoria, imagen, fecha_creacion, talla, genero FROM productos WHERE genero = 'Masculino' AND stock > 0")
        productos = cursor.fetchall()
    conexion.close()
    return productos

def obtener_productos_mujer():
    conexion = obtener_conexion()
    productos = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id_producto, nombre_producto, descripcion, precio, stock, id_categoria, imagen, fecha_creacion, talla, genero FROM productos WHERE genero = 'Femenino' AND stock > 0")
        productos = cursor.fetchall()
    conexion.close()
    return productos

def insertar_nuevo_pedido(id_usuario):
    conexion = obtener_conexion()
    pedido = None
    with conexion.cursor() as cursor:
        cursor.execute("INSERT INTO pedidos (id_usuario, fecha_creacion, total, estado) VALUES (%s, CURRENT_TIMESTAMP, 0, 'pendiente')", (id_usuario,))
        pedido = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return pedido

def guardar_detalle(id_producto, cantidad, id_pedido):
    conexion = obtener_conexion()
    try:
        with conexion.cursor(DictCursor) as cursor:
            cursor.execute("""
                INSERT INTO detalles_pedido (id_pedido, id_producto, cantidad)
                VALUES (%s, %s, %s)
            """, (id_pedido, id_producto, cantidad))

            cursor.execute("""
                SELECT SUM(p.precio * dp.cantidad) AS total_pedido
                FROM detalles_pedido dp
                JOIN productos p ON dp.id_producto = p.id_producto
                WHERE dp.id_pedido = %s
            """, (id_pedido,))
            resultado = cursor.fetchone()

            if resultado and resultado['total_pedido'] is not None:
                total_pedido = resultado['total_pedido']
            else:
                total_pedido = Decimal('0.00')

            cursor.execute("""
                UPDATE pedidos SET total = %s WHERE id_pedido = %s
            """, (total_pedido, id_pedido))

            cursor.execute("""
                UPDATE productos SET stock = stock - %s WHERE id_producto = %s
            """, (cantidad, id_producto))

            conexion.commit()
    except Exception as e:
        print("Ocurrió un error al procesar el detalle del pedido:", e)
        conexion.rollback()
    finally:
        conexion.close()

def obtener_nombre_categoria_api():
    conexion = obtener_conexion()
    categorias = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id_categoria, nombre, descripcion, fecha_creacion FROM categorias")
        categorias = cursor.fetchall()
    conexion.close()
    return categorias

def obtener_nombre_categoria_por_id(id):
    conexion = obtener_conexion()
    categoria = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id_categoria, nombre, descripcion, fecha_creacion FROM categorias WHERE id_categoria = %s", (id,))
        categoria = cursor.fetchall()
    conexion.close()
    return categoria

def insertar_categoria(nombre, descripcion):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("INSERT INTO categorias (nombre, descripcion, fecha_creacion) VALUES (%s, %s, CURRENT_DATE())", (nombre, descripcion))
        ultimo_id = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return ultimo_id

def actualizar_categoria(nombre, descripcion, fecha_creacion, id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE categorias SET nombre = %s, descripcion = %s, fecha_creacion = %s WHERE id_categoria = %s", (nombre, descripcion, fecha_creacion, id))
        filas_afectadas = cursor.rowcount
    conexion.commit()
    conexion.close()
    return filas_afectadas > 0

def eliminar_categoria(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("DELETE FROM categorias WHERE id_categoria = %s", (id,))
        filas_afectadas = cursor.rowcount
    conexion.commit()
    conexion.close()
    return filas_afectadas > 0

def obtener_insumos():
    conexion = obtener_conexion()
    insumos = []
    with conexion.cursor() as cursor:
        query = "SELECT * FROM insumos_materiales;"
        cursor.execute(query)
        insumos = cursor.fetchall()
    conexion.close()
    return insumos