from flask import jsonify, request
from bd_conexion import obtener_conexion

def obtener_todas_cuentas():
    conexion = obtener_conexion()
    cuentas = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            WITH cuenta_jerarquia AS (
                -- Seleccionamos todas las cuentas, verificamos si tienen subcuentas, y añadimos estado y categoría
                SELECT 
                    c1.cuenta_id AS id_cuenta,
                    c1.codigo AS codigo_cuenta,
                    c1.descripcion AS descripcion_cuenta,
                    c1.cuenta_padre AS cuenta_padre,
                    c1.estado AS estado_cuenta, -- Añadimos el estado de la cuenta
                    c1.categoria AS categoria_cuenta, -- Añadimos la categoría de la cuenta
                    CASE 
                        WHEN EXISTS (SELECT 1 FROM cuentas c2 WHERE c2.cuenta_padre = c1.cuenta_id)
                        THEN TRUE
                        ELSE FALSE
                    END AS tiene_subcuentas
                FROM cuentas c1
            )
            SELECT 
                id_cuenta,
                codigo_cuenta,
                descripcion_cuenta,
                cuenta_padre,
                estado_cuenta, -- Mostramos el estado de la cuenta
                categoria_cuenta, -- Mostramos la categoría de la cuenta
                tiene_subcuentas
            FROM cuenta_jerarquia
            ORDER BY codigo_cuenta;
        """)
        cuentas = cursor.fetchall()
    conexion.close()
    return cuentas

def obtener_cuentas_por_categoria(categoria):
    """
    Función para obtener las cuentas principales de una categoría específica.
    """
    conexion = obtener_conexion()
    cuentas = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT cuenta_id, codigo, descripcion 
            FROM cuentas 
            WHERE categoria = %s AND cuenta_padre IS NULL
            ORDER BY codigo;
        """, (categoria,))
        cuentas = cursor.fetchall()
    
    conexion.close()
    return cuentas

def obtener_cuentas_por_categoria_endpoint():
    """
    Endpoint para manejar la solicitud desde el frontend y devolver cuentas como JSON.
    """
    data = request.get_json()
    id_categoria = data.get('categoria')

    if not id_categoria:
        print("No se proporcionó una categoría")
        return jsonify([])  # Si no se proporciona una categoría, devolver una lista vacía

    conexion = obtener_conexion()
    cuentas = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT cuenta_id, codigo, descripcion 
                FROM cuentas 
                WHERE LOWER(categoria) = LOWER(%s) AND cuenta_padre IS NULL
                ORDER BY codigo;
            """, (id_categoria,))
            cuentas = cursor.fetchall()
            print(f"Datos obtenidos para la categoría {id_categoria}: {cuentas}")
    except Exception as e:
        print(f"Error al obtener cuentas por categoría: {e}")
    finally:
        conexion.close()

    # Transformar las cuentas en una lista de diccionarios
    cuentas_json = [{'id': c[0], 'codigo': c[1], 'descripcion': c[2]} for c in cuentas]
    return jsonify(cuentas_json)


def verificar_existencia_cuenta(codigo, categoria):
    conexion = obtener_conexion()
    cuenta_existe = False
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT 1 FROM cuentas WHERE codigo = %s AND LOWER(categoria) = LOWER(%s);
        """, (codigo, categoria))
        cuenta_existe = cursor.fetchone() is not None
    conexion.close()
    return cuenta_existe

def obtener_ultimo_codigo_subcuenta(cuenta_padre):
    conexion = obtener_conexion()
    ultimo_codigo = None
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT MAX(CAST(codigo AS INTEGER)) FROM cuentas WHERE cuenta_padre = %s;
        """, (cuenta_padre,))
        ultimo_codigo = cursor.fetchone()[0]
    conexion.close()
    return ultimo_codigo


def obtener_nivel_cuenta(codigo):
    """
    Función para obtener el nivel de una cuenta basado en su código.
    """
    if len(codigo) <= 2:  # Nivel 1 (ej. 10, 20)
        return 1
    elif len(codigo) <= 4:  # Nivel 2 (ej. 101, 102)
        return 2
    elif len(codigo) <= 6:  # Nivel 3 (ej. 1011, 1021)
        return 3
    else:  # Niveles más profundos
        return 4

def validar_nivel_cuenta(codigo, cuenta_padre):
    """
    Valida que el código de la nueva cuenta pertenezca al rango de la cuenta padre.
    """
    nivel_cuenta = obtener_nivel_cuenta(codigo)
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT codigo, nivel FROM cuentas WHERE cuenta_id = %s;
            """, (cuenta_padre,))
            cuenta_padre_info = cursor.fetchone()

            if cuenta_padre_info is None:
                return False, "La cuenta padre no existe."

            codigo_padre, nivel_padre = cuenta_padre_info

            # Verificar si el código de la subcuenta es una extensión válida del código padre
            if not codigo.startswith(codigo_padre):
                return False, f"El código '{codigo}' no pertenece al rango de la cuenta padre '{codigo_padre}'."

            # Verificar si el nivel es adecuado
            if nivel_cuenta != nivel_padre + 1:
                return False, f"El código '{codigo}' no corresponde al nivel {nivel_padre + 1} esperado."

            return True, ""
    finally:
        conexion.close()



def añadir_cuenta():
    data = request.get_json()
    codigo = data.get('codigo')
    descripcion = data.get('descripcion')
    cuenta_padre = data.get('cuenta_padre')
    estado = data.get('estado')
    categoria = data.get('categoria')

    if not categoria or not descripcion or not codigo:
        return jsonify({'error': 'Faltan datos obligatorios'}), 400

    # Verificar si ya existe una cuenta con el mismo código y categoría
    if verificar_existencia_cuenta(codigo, categoria):
        return jsonify({'error': 'La cuenta ya existe en esta categoría'}), 400

    nivel = obtener_nivel_cuenta(codigo)

    # Si hay cuenta padre, validar el código y el nivel
    if cuenta_padre:
        valido, mensaje_error = validar_nivel_cuenta(codigo, cuenta_padre)
        if not valido:
            return jsonify({'error': mensaje_error}), 400

    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO cuentas (codigo, descripcion, cuenta_padre, estado, categoria, nivel)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING cuenta_id;
            """, (codigo, descripcion, cuenta_padre, estado, categoria, nivel))
            nueva_cuenta_id = cursor.fetchone()[0]
            conexion.commit()

        return jsonify({
            'message': 'Cuenta añadida exitosamente',
            'cuenta': {
                'id': nueva_cuenta_id,
                'codigo': codigo,
                'descripcion': descripcion,
                'cuenta_padre': cuenta_padre,
                'estado': estado,
                'categoria': categoria
            }
        }), 201
    except Exception as e:
        conexion.rollback()
        return jsonify({'error': f'Error al añadir la cuenta: {str(e)}'}), 500
    finally:
        conexion.close()



