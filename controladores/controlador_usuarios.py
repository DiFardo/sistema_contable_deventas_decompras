from bd_conexion import obtener_conexion

def obtener_usuario(dni):
    conexion = obtener_conexion()
    usuario = None
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT u.id, u.dni, u.pass, u.token, 
                   CONCAT(p.nombre, ' ', p.apellido) AS nombre_completo, 
                   p.rol, 
                   p.imagen  
            FROM usuarios u
            JOIN personas p ON u.id_persona = p.id
            WHERE u.dni = %s
            """, (dni,))
        usuario = cursor.fetchone()
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
            SELECT p.nombre, p.apellido, p.dni, p.rol, p.imagen
            FROM personas p
            JOIN usuarios u ON p.id = u.id_persona
            WHERE u.dni = %s
            """, (dni,))
        perfil = cursor.fetchone()
    conexion.close()
    return perfil

# Nueva función para obtener la imagen de perfil
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

# Nueva función para eliminar la imagen de perfil
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
                   p.rol
            FROM usuarios u
            JOIN personas p ON u.dni = p.dni
            WHERE u.dni = %s
            """, (dni,))
        usuario = cursor.fetchone()
    conexion.close()
    return usuario



def obtener_todos_usuarios():
    conexion = obtener_conexion()
    usuarios = []
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT u.dni, p.nombre, p.apellido, p.rol
            FROM usuarios u
            JOIN personas p ON u.dni = p.dni
            """
        )
        resultados = cursor.fetchall()
        for row in resultados:
            usuario = {
                'dni': row[0],
                'nombre': row[1],
                'apellido': row[2],
                'rol': row[3]
            }
            usuarios.append(usuario)
    conexion.close()
    return usuarios

def agregar_usuario(dni, nombre, apellido, rol, password):
    import hashlib  # Asegúrate de importar hashlib si no lo has hecho
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Verificar si el DNI ya existe en 'personas'
            cursor.execute("SELECT id FROM personas WHERE dni = %s", (dni,))
            if cursor.fetchone():
                print("El DNI ya existe en la base de datos.")
                return False

            # Insertar en la tabla 'personas'
            cursor.execute(
                "INSERT INTO personas (nombre, apellido, dni, rol) VALUES (%s, %s, %s, %s)",
                (nombre, apellido, dni, rol)
            )
            conexion.commit()

            # Obtener el id de la nueva persona
            cursor.execute("SELECT id FROM personas WHERE dni = %s", (dni,))
            id_persona = cursor.fetchone()[0]

            # Hash de la contraseña
            h = hashlib.new("sha256")
            h.update(password.encode('utf-8'))
            hashed_password = h.hexdigest().lower()

            # Insertar en la tabla 'usuarios'
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

def editar_usuario(dni, nombre, apellido, rol):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Actualizar en la tabla 'personas'
            cursor.execute(
                "UPDATE personas SET nombre = %s, apellido = %s, rol = %s WHERE dni = %s",
                (nombre, apellido, rol, dni)
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
            # Obtener el id_persona
            cursor.execute("SELECT id_persona FROM usuarios WHERE dni = %s", (dni,))
            result = cursor.fetchone()
            if not result:
                print("El usuario no existe.")
                return False
            id_persona = result[0]

            # Eliminar de la tabla 'usuarios'
            cursor.execute("DELETE FROM usuarios WHERE dni = %s", (dni,))
            # Eliminar de la tabla 'personas'
            cursor.execute("DELETE FROM personas WHERE id = %s", (id_persona,))
            conexion.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()

def obtener_datos_persona(dni):
    conexion = obtener_conexion()
    usuario = None
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT u.dni, u.pass, u.token, 
                   CONCAT(p.nombre, ' ', p.apellido) AS nombre_completo, 
                   p.rol
            FROM usuarios u
            JOIN personas p ON u.dni = p.dni
            WHERE u.dni = %s
            """, (dni,))
        usuario = cursor.fetchone()
    conexion.close()
    return usuario



def obtener_todos_usuarios():
    conexion = obtener_conexion()
    usuarios = []
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT u.dni, p.nombre, p.apellido, p.rol
            FROM usuarios u
            JOIN personas p ON u.dni = p.dni
            """
        )
        resultados = cursor.fetchall()
        for row in resultados:
            usuario = {
                'dni': row[0],
                'nombre': row[1],
                'apellido': row[2],
                'rol': row[3]
            }
            usuarios.append(usuario)
    conexion.close()
    return usuarios

def agregar_usuario(dni, nombre, apellido, rol, password):
    import hashlib  # Asegúrate de importar hashlib si no lo has hecho
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Verificar si el DNI ya existe en 'personas'
            cursor.execute("SELECT id FROM personas WHERE dni = %s", (dni,))
            if cursor.fetchone():
                print("El DNI ya existe en la base de datos.")
                return False

            # Insertar en la tabla 'personas'
            cursor.execute(
                "INSERT INTO personas (nombre, apellido, dni, rol) VALUES (%s, %s, %s, %s)",
                (nombre, apellido, dni, rol)
            )
            conexion.commit()

            # Obtener el id de la nueva persona
            cursor.execute("SELECT id FROM personas WHERE dni = %s", (dni,))
            id_persona = cursor.fetchone()[0]

            # Hash de la contraseña
            h = hashlib.new("sha256")
            h.update(password.encode('utf-8'))
            hashed_password = h.hexdigest().lower()

            # Insertar en la tabla 'usuarios'
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

def editar_usuario(dni, nombre, apellido, rol):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Actualizar en la tabla 'personas'
            cursor.execute(
                "UPDATE personas SET nombre = %s, apellido = %s, rol = %s WHERE dni = %s",
                (nombre, apellido, rol, dni)
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
            # Obtener el id_persona
            cursor.execute("SELECT id_persona FROM usuarios WHERE dni = %s", (dni,))
            result = cursor.fetchone()
            if not result:
                print("El usuario no existe.")
                return False
            id_persona = result[0]

            # Eliminar de la tabla 'usuarios'
            cursor.execute("DELETE FROM usuarios WHERE dni = %s", (dni,))
            # Eliminar de la tabla 'personas'
            cursor.execute("DELETE FROM personas WHERE id = %s", (id_persona,))
            conexion.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()