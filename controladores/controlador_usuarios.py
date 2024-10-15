from bd_conexion import obtener_conexion

def obtener_usuario(dni):
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
