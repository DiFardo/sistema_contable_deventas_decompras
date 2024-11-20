from bd_conexion import obtener_conexion
import hashlib
from psycopg2.extras import RealDictCursor

def obtener_roles():
    conexion = obtener_conexion()
    roles = []
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, nombre, descripcion 
            FROM roles
            WHERE estado = true
            """
        )
        roles = cursor.fetchall()
    conexion.close()
    return roles

def obtener_descripcion_rol_por_nombre(nombre_rol):
    conexion = obtener_conexion()
    descripcion = None
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT descripcion 
            FROM roles
            WHERE nombre = %s AND estado = true
            """, (nombre_rol,)
        )
        resultado = cursor.fetchone()
        if resultado:
            descripcion = resultado[0]
    conexion.close()
    return descripcion

def obtener_usuario(dni):
    conexion = obtener_conexion()
    usuario = None
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT u.id AS usuario_id, u.dni, u.pass, u.token, 
                   CONCAT(p.nombre, ' ', p.apellido) AS nombre_completo, 
                   r.nombre AS rol_nombre, 
                   p.imagen  
            FROM usuarios u
            JOIN personas p ON u.id_persona = p.id
            LEFT JOIN roles r ON p.id_rol = r.id
            WHERE u.dni = %s
            """, (dni,))
        usuario = cursor.fetchone()
    conexion.close()
    return usuario

def obtener_usuario_idrol(dni):
    conexion = obtener_conexion()
    usuario = None
    with conexion.cursor(cursor_factory=RealDictCursor) as cursor:  # Usa RealDictCursor
        cursor.execute(
            """
            SELECT u.id AS usuario_id, u.dni, u.pass, u.token, 
                   CONCAT(p.nombre, ' ', p.apellido) AS nombre_completo, 
                   r.id AS rol_id, 
                   p.imagen  
            FROM usuarios u
            JOIN personas p ON u.id_persona = p.id
            LEFT JOIN roles r ON p.id_rol = r.id
            WHERE u.dni = %s
            """, (dni,)
        )
        usuario = cursor.fetchone()  # Devuelve un diccionario
    conexion.close()
    return usuario

def actualizartoken_usuario(dni, token):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE usuarios SET token = %s WHERE dni = %s",
                       (token, dni))
    conexion.commit()
    conexion.close()

def obtener_usuarioporid(id):
    conexion = obtener_conexion()
    usuario = None
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT u.id, u.dni, u.pass, u.token, 
                   CONCAT(p.nombre, ' ', p.apellido) AS nombre_completo, 
                   r.nombre AS rol
            FROM usuarios u
            JOIN personas p ON u.id_persona = p.id
            LEFT JOIN roles r ON p.id_rol = r.id
            WHERE u.id = %s
            """, (id,))
        usuario = cursor.fetchone()
    conexion.close()
    return usuario

def eliminar_token_usuario(dni):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE usuarios SET token = '' WHERE dni = %s", (dni,))
    conexion.commit()
    conexion.close()

def obtener_detalles_perfil(dni):
    conexion = obtener_conexion()
    perfil = None
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT 
                p.nombre, 
                p.apellido, 
                p.dni, 
                r.nombre AS rol, 
                p.imagen
            FROM 
                personas p
            LEFT JOIN 
                roles r ON p.id_rol = r.id
            JOIN 
                usuarios u ON p.id = u.id_persona
            WHERE 
                u.dni = %s
            """, (dni,))
        perfil = cursor.fetchone()
    conexion.close()
    return perfil

def obtener_imagen_perfil(dni):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT imagen FROM personas
            WHERE dni = %s
        """, (dni,))
        imagen = cursor.fetchone()[0]
    conexion.close()
    return imagen

def actualizar_imagen_perfil(dni, filename):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("""
            UPDATE personas 
            SET imagen = %s 
            WHERE dni = %s
        """, (filename, dni))
    conexion.commit()
    conexion.close()

def eliminar_imagen_perfil(dni):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("""
            UPDATE personas SET imagen = NULL
            WHERE dni = %s
        """, (dni,))
    conexion.commit()
    conexion.close()

def actualizar_perfil_usuario(dni, nombres, apellidos):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("""
            UPDATE personas
            SET nombre = %s, apellido = %s
            WHERE dni = %s
        """, (nombres, apellidos, dni))
    conexion.commit()
    conexion.close()

def obtener_datos_persona(dni):
    conexion = obtener_conexion()
    usuario = None
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT u.dni, u.pass, u.token, 
                   CONCAT(p.nombre, ' ', p.apellido) AS nombre_completo, 
                   r.nombre AS rol
            FROM usuarios u
            JOIN personas p ON u.id_persona = p.id
            LEFT JOIN roles r ON p.id_rol = r.id
            WHERE u.dni = %s
            """, (dni,)
        )
        usuario = cursor.fetchone()
    conexion.close()
    return usuario

def obtener_todos_usuarios():
    conexion = obtener_conexion()
    usuarios = []
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT 
                u.dni, 
                p.nombre, 
                p.apellido, 
                r.nombre AS rol
            FROM usuarios u
            JOIN personas p ON u.id_persona = p.id
            LEFT JOIN roles r ON p.id_rol = r.id
            """
        )
        resultados = cursor.fetchall()
        for row in resultados:
            usuario = {
                'dni': row[0],
                'nombre': row[1],
                'apellido': row[2],
                'rol': row[3] if row[3] else 'Sin rol asignado'
            }
            usuarios.append(usuario)
    conexion.close()
    return usuarios

def agregar_usuario(dni, nombre, apellido, id_rol, password):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id FROM personas WHERE dni = %s", (dni,))
            if cursor.fetchone():
                print("El DNI ya existe en la base de datos.")
                return False
            cursor.execute(
                "INSERT INTO personas (nombre, apellido, dni, id_rol) VALUES (%s, %s, %s, %s)",
                (nombre, apellido, dni, id_rol)
            )
            conexion.commit()
            cursor.execute("SELECT id FROM personas WHERE dni = %s", (dni,))
            id_persona = cursor.fetchone()[0]
            h = hashlib.new("sha256")
            h.update(password.encode('utf-8'))
            hashed_password = h.hexdigest().lower()
            cursor.execute(
                "INSERT INTO usuarios (dni, pass, token, id_persona) VALUES (%s, %s, '', %s)",
                (dni, hashed_password, id_persona)
            )
            conexion.commit()
        return True
    except Exception as e:
        print(f"Error al agregar usuario: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()

def editar_usuario(dni, nombre, apellido, id_rol):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "UPDATE personas SET nombre = %s, apellido = %s, id_rol = %s WHERE dni = %s",
                (nombre, apellido, id_rol, dni)
            )
            conexion.commit()
        return True
    except Exception as e:
        print(f"Error al editar usuario: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()

def eliminar_usuario(dni):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id_persona FROM usuarios WHERE dni = %s", (dni,))
            result = cursor.fetchone()
            if not result:
                print("El usuario no existe.")
                return False
            id_persona = result[0]
            cursor.execute("DELETE FROM usuarios WHERE dni = %s", (dni,))
            cursor.execute("DELETE FROM personas WHERE id = %s", (id_persona,))
            conexion.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()

def verificar_dni(dni):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT 1 FROM usuarios WHERE dni = %s", (dni,))
        resultado = cursor.fetchone()
    conexion.close()
    return resultado is not None