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
