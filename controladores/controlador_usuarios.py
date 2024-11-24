from bd_conexion import obtener_conexion
import hashlib

def obtener_usuario(dni):
    conexion = obtener_conexion()
    usuario = None
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT u.id AS usuario_id, 
                   u.dni, 
                   u.pass, 
                   u.token, 
                   CONCAT(p.nombre, ' ', p.apellido) AS nombre_completo, 
                   r.nombre AS rol_nombre, 
                   r.descripcion AS rol_descripcion, 
                   p.imagen  
            FROM usuarios u
            JOIN personas p ON u.id_persona = p.id
            JOIN roles r ON p.id_rol = r.id
            WHERE u.dni = %s
            """, 
            (dni,)
        )
        usuario = cursor.fetchone()
    conexion.close()
    return usuario


def obtener_rol_por_usuario(dni):
    conexion = obtener_conexion()
    rol = None
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT r.nombre AS rol_nombre
                FROM usuarios u
                JOIN personas p ON u.id_persona = p.id
                JOIN roles r ON p.id_rol = r.id
                WHERE u.dni = %s
                """,
                (dni,)
            )
            rol = cursor.fetchone()
    finally:
        conexion.close()
    return rol


def obtener_nombres_roles():
    """
    Obtiene los nombres de todos los roles disponibles en la base de datos.

    Returns:
        list: Una lista de strings con los nombres de los roles.
    """
    conexion = obtener_conexion()
    nombres_roles = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT nombre FROM roles")
            resultados = cursor.fetchall()
            # Extraer los nombres de los resultados
            nombres_roles = [fila[0] for fila in resultados]
    except Exception as e:
        print(f"Error al obtener los nombres de los roles: {e}")
    finally:
        conexion.close()
    
    return nombres_roles


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
                   p.rol 
            FROM usuarios u
            JOIN personas p ON u.id_persona = p.id
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
                r.nombre AS rol_nombre, 
                r.descripcion AS rol_descripcion, 
                p.imagen
            FROM personas p
            JOIN usuarios u ON p.id = u.id_persona
            JOIN roles r ON p.id_rol = r.id
            WHERE u.dni = %s
            """, 
            (dni,)
        )
        perfil = cursor.fetchone()
    conexion.close()
    return perfil

def obtener_descripcion_rol(rol_nombre):
    """
    Obtiene la descripción del rol desde la base de datos usando el nombre del rol.

    Args:
        rol_nombre (str): Nombre del rol.

    Returns:
        str: Descripción del rol o un mensaje indicando que no se encontró.
    """
    conexion = obtener_conexion()
    descripcion = None
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT descripcion 
                FROM roles
                WHERE nombre = %s
                """,
                (rol_nombre,)
            )
            resultado = cursor.fetchone()
            if resultado:
                descripcion = resultado[0]  # Asume que solo hay una columna: 'descripcion'
            else:
                descripcion = "Descripción no encontrada."
    except Exception as e:
        print(f"Error al obtener la descripción del rol: {e}")
        descripcion = "Error al buscar la descripción."
    finally:
        conexion.close()
    return descripcion

def obtener_todas_las_descripciones():
    """
    Obtiene todas las descripciones de roles desde la base de datos.

    Returns:
        dict: Diccionario con los nombres de roles como claves y sus descripciones como valores.
    """
    conexion = obtener_conexion()
    descripciones = {}
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT nombre, descripcion
                FROM roles
                """
            )
            resultados = cursor.fetchall()
            descripciones = {row[0]: row[1] for row in resultados}  # Construir diccionario
    except Exception as e:
        print(f"Error al obtener todas las descripciones de roles: {e}")
    finally:
        conexion.close()
    return descripciones




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
            SELECT 
                u.dni, 
                u.pass, 
                u.token, 
                CONCAT(p.nombre, ' ', p.apellido) AS nombre_completo, 
                r.nombre AS rol_nombre, 
                r.descripcion AS rol_descripcion
            FROM usuarios u
            JOIN personas p ON u.id_persona = p.id
            JOIN roles r ON p.id_rol = r.id
            WHERE u.dni = %s
            """, 
            (dni,)
        )
        usuario = cursor.fetchone()
    conexion.close()
    return usuario


def obtener_todos_usuarios():
    """
    Obtiene una lista de todos los usuarios, incluyendo información detallada como nombre completo y rol.

    Returns:
        list: Una lista de diccionarios donde cada diccionario representa un usuario.
    """
    conexion = obtener_conexion()
    usuarios = []
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT 
                u.dni, 
                p.nombre, 
                p.apellido, 
                r.nombre AS rol_nombre, 
                r.descripcion AS rol_descripcion
            FROM usuarios u
            JOIN personas p ON u.id_persona = p.id
            JOIN roles r ON p.id_rol = r.id
            """
        )
        resultados = cursor.fetchall()
        for row in resultados:
            usuario = {
                'dni': row[0],
                'nombre': row[1],
                'apellido': row[2],
                'rol_nombre': row[3],
                'rol_descripcion': row[4]
            }
            usuarios.append(usuario)
    conexion.close()
    return usuarios


def agregar_usuario(dni, nombre, apellido, id_rol, password):
    """
    Agrega un nuevo usuario a la base de datos, incluyendo su información personal y credenciales.

    Args:
        dni (str): DNI del usuario.
        nombre (str): Nombre del usuario.
        apellido (str): Apellido del usuario.
        id_rol (int): ID del rol del usuario.
        password (str): Contraseña del usuario.

    Returns:
        bool: True si el usuario fue agregado exitosamente, False en caso contrario.
    """
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Verificar si el DNI ya existe en la tabla personas
            cursor.execute("SELECT id FROM personas WHERE dni = %s", (dni,))
            if cursor.fetchone():
                print("El DNI ya existe en la base de datos.")
                return False
            
            # Insertar datos en la tabla personas
            cursor.execute(
                """
                INSERT INTO personas (nombre, apellido, dni, id_rol) 
                VALUES (%s, %s, %s, %s)
                """,
                (nombre, apellido, dni, id_rol)
            )
            conexion.commit()

            # Obtener el ID de la persona recién insertada
            cursor.execute("SELECT id FROM personas WHERE dni = %s", (dni,))
            id_persona = cursor.fetchone()[0]

            # Hashear la contraseña
            h = hashlib.new("sha256")
            h.update(password.encode('utf-8'))
            hashed_password = h.hexdigest().lower()

            # Insertar datos en la tabla usuarios
            cursor.execute(
                """
                INSERT INTO usuarios (dni, pass, token, id_persona) 
                VALUES (%s, %s, '', %s)
                """,
                (dni, hashed_password, id_persona)
            )
            conexion.commit()

        return True
    except Exception as e:
        print(f"Error al agregar usuario: {e}")
        conexion.rollback()  # Revertir cambios si ocurre un error
        return False
    finally:
        conexion.close()  # Asegurar el cierre de la conexión


def editar_usuario(dni, nombre, apellido, id_rol):
    """
    Edita la información de un usuario en la base de datos.

    Args:
        dni (str): DNI del usuario.
        nombre (str): Nuevo nombre del usuario.
        apellido (str): Nuevo apellido del usuario.
        id_rol (int): Nuevo ID del rol del usuario.

    Returns:
        bool: True si el usuario fue editado exitosamente, False en caso contrario.
    """
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Actualizar los datos de la persona en la tabla personas
            cursor.execute(
                """
                UPDATE personas 
                SET nombre = %s, apellido = %s, id_rol = %s 
                WHERE dni = %s
                """,
                (nombre, apellido, id_rol, dni)
            )
            conexion.commit()

        return True
    except Exception as e:
        print(f"Error al editar usuario: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()  # Asegurar el cierre de la conexión


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