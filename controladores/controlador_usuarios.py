from bd_conexion import obtener_conexion
import hashlib
from psycopg2.extras import RealDictCursor

def obtener_ids_permisos_por_nombre(nombres_permisos):
    conexion = obtener_conexion()
    permisos_ids = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT id
            FROM public.permisos
            WHERE nombre = ANY(%s)
        """, (nombres_permisos,))
        resultados = cursor.fetchall()
        permisos_ids = [row[0] for row in resultados]
    conexion.close()
    return permisos_ids

def obtener_usuario_id(dni):
    conexion = obtener_conexion()
    usuario_id = None
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM usuarios WHERE dni = %s", (dni,)
        )
        usuario_id = cursor.fetchone()
    conexion.close()
    return usuario_id[0] if usuario_id else None

def eliminar_permisos(usuario_id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(
            "DELETE FROM usuarios_permisos WHERE id_usuario = %s", (usuario_id,)
        )
        conexion.commit()
    conexion.close()

def agregar_permiso(usuario_id, permiso_id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("""
            INSERT INTO public.usuarios_permisos (id_usuario, id_permiso)
            VALUES (%s, %s)
        """, (usuario_id, permiso_id))
    conexion.commit()
    conexion.close()

def obtener_permisos_usuario(dni):
    conexion = obtener_conexion()
    permisos = []
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT p.nombre AS permiso_nombre
            FROM public.usuarios u
            JOIN public.personas ps ON u.id_persona = ps.id
            JOIN public.roles r ON ps.id_rol = r.id
            JOIN public.roles_permisos rp ON r.id = rp.rol_id
            JOIN public.permisos p ON rp.permiso_id = p.id
            UNION
            SELECT DISTINCT p.nombre AS permiso_nombre
            FROM public.usuarios u
            JOIN public.usuarios_permisos up ON u.id = up.id_usuario
            JOIN public.permisos p ON up.id_permiso = p.id
            WHERE u.dni = %s;
            """,(dni,)
        )
        permisos = cursor.fetchall()
    conexion.close()
    return [permiso[0] for permiso in permisos]


def obtener_permisos_por_rol(id_rol):
    conexion = obtener_conexion()
    permisos = []
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT p.nombre
            FROM public.permisos p
            INNER JOIN public.roles_permisos rp ON p.id = rp.permiso_id
            WHERE rp.rol_id = %s
            """,
            (id_rol,)
        )
        permisos = cursor.fetchall()
    conexion.close()
    return [permiso[0] for permiso in permisos]

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
                   p.imagen,
                   r.id  
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
    with conexion.cursor(cursor_factory=RealDictCursor) as cursor:
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
        cursor.execute("""
            SELECT 
                u.dni, 
                p.nombre, 
                p.apellido, 
                r.nombre AS rol,
                r.id AS rol_id,
                ARRAY(
                    SELECT p.nombre
                    FROM public.roles_permisos rp
                    JOIN public.permisos p ON rp.permiso_id = p.id
                    WHERE rp.rol_id = r.id
                ) || ARRAY(
                    SELECT p.nombre
                    FROM public.usuarios_permisos up
                    JOIN public.permisos p ON up.id_permiso = p.id
                    WHERE up.id_usuario = u.id
                ) AS permisos
            FROM usuarios u
            JOIN personas p ON u.id_persona = p.id
            LEFT JOIN roles r ON p.id_rol = r.id
        """)
        resultados = cursor.fetchall()
        for row in resultados:
            usuario = {
                'dni': row[0],
                'nombre': row[1],
                'apellido': row[2],
                'rol': row[3] if row[3] else 'Sin rol asignado',
                'rol_id': row[4] if row[4] else None,
                'permisos': row[5]
            }
            usuarios.append(usuario)
    conexion.close()
    return usuarios

def agregar_usuario(dni, nombre, apellido, id_rol, password, permissions):
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
            if permissions:
                for permiso in permissions:
                    cursor.execute(
                        "SELECT id FROM permisos WHERE nombre = %s", (permiso,)
                    )
                    permiso_id = cursor.fetchone()
                    if permiso_id:
                        cursor.execute(
                            "INSERT INTO usuarios_permisos (id_usuario, id_permiso) VALUES (%s, %s)",
                            (id_persona, permiso_id[0])
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

def obtener_notificaciones(rol):
    """
    Obtiene notificaciones dependiendo del rol del usuario.
    Solo los roles Administrador y Contador tendrán acceso a las notificaciones.
    """
    if rol not in ['Administrador', 'Contador']:
        return []  # Si no es Administrador o Contador, no hay notificaciones.

    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT mensaje, url, leido, creado_en
                FROM notificaciones
                WHERE leido = false
                ORDER BY creado_en DESC
            """)
            return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener notificaciones: {e}")
        return []
    finally:
        conexion.close()
