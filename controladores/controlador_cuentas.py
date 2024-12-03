from flask import jsonify, request
from bd_conexion import obtener_conexion
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from io import BytesIO
from flask import send_file, jsonify

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

def obtener_cuenta_padre(codigo):
    conexion = obtener_conexion()
    cuenta_padre = None
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT cuenta_id, codigo
            FROM cuentas
            WHERE %s LIKE CONCAT(codigo, '%%')
            ORDER BY LENGTH(codigo) DESC
            LIMIT 1;
        """, (codigo,))
        cuenta_padre = cursor.fetchone()
    conexion.close()
    return cuenta_padre

# Variable global para almacenar las cuentas nuevas añadidas
cuentas_nuevas = set()

def añadir_cuenta():
    data = request.get_json()
    codigo = data.get('codigo')
    descripcion = data.get('descripcion')
    estado = data.get('estado')
    categoria = data.get('categoria')
    nivel_seleccionado = int(data.get('nivel', 2))  # Nivel predeterminado a 2 si no se proporciona

    if not categoria or not descripcion or not codigo:
        return jsonify({'error': 'Faltan datos obligatorios'}), 400

    # Verificar si ya existe una cuenta con el mismo código y categoría
    if verificar_existencia_cuenta(codigo, categoria):
        return jsonify({'error': 'El código ya existe en esta categoría.'}), 400

    # Calcular cuenta padre
    cuenta_padre = obtener_cuenta_padre(codigo)
    longitud_permitida = {2: 3, 3: 4, 4: 5}  # Longitud de código para cada nivel

    # Validar la longitud del código según el nivel seleccionado
    if len(codigo) != longitud_permitida.get(nivel_seleccionado, 3):  # 3 dígitos como longitud predeterminada
        return jsonify({'error': f'El código debe tener {longitud_permitida[nivel_seleccionado]} dígitos para el nivel seleccionado.'}), 400

    # Verificar que el código pertenezca a la cuenta padre
    if cuenta_padre:
        cuenta_padre_id, codigo_padre = cuenta_padre
        if not codigo.startswith(codigo_padre):
            return jsonify({'error': f"El código '{codigo}' no pertenece al rango de la cuenta padre '{codigo_padre}'."}), 400
    else:
        cuenta_padre_id = None

    # Insertar cuenta en la base de datos
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO cuentas (codigo, descripcion, cuenta_padre, estado, categoria, nivel)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING cuenta_id;
            """, (codigo, descripcion, cuenta_padre_id, estado, categoria, nivel_seleccionado))
            nueva_cuenta_id = cursor.fetchone()[0]

            # Añadir la notificación
            mensaje = f"Se ha añadido una nueva cuenta: {descripcion} (Código: {codigo})"
            url = "/cuentas"
            cursor.execute("""
                INSERT INTO notificaciones (mensaje, url, leido)
                VALUES (%s, %s, FALSE);
            """, (mensaje, url))

            conexion.commit()

            # Agregar la nueva cuenta al conjunto global
            cuentas_nuevas.add(codigo)

        return jsonify({
            'message': 'Cuenta añadida exitosamente',
            'cuenta': {
                'id': nueva_cuenta_id,
                'codigo': codigo,
                'descripcion': descripcion,
                'cuenta_padre': cuenta_padre_id,
                'estado': estado,
                'categoria': categoria
            },
            'cuentas_nuevas': list(cuentas_nuevas)  # Devolver todas las cuentas nuevas añadidas
        }), 201
    except Exception as e:
        conexion.rollback()
        return jsonify({'error': f'Error al añadir la cuenta: {str(e)}'}), 500
    finally:
        conexion.close()

def editar_cuenta():
    data = request.get_json()
    codigo = data.get('codigo')  # Código único de la cuenta
    descripcion = data.get('descripcion')
    estado = data.get('estado')

    if not codigo or not descripcion:
        return jsonify({'error': 'Faltan datos obligatorios'}), 400

    # Conexión a la base de datos
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Verificar si la cuenta existe
            cursor.execute("SELECT cuenta_id FROM cuentas WHERE codigo = %s;", (codigo,))
            cuenta_existente = cursor.fetchone()

            if not cuenta_existente:
                return jsonify({'error': 'La cuenta no existe.'}), 404

            # Actualizar solo la descripción y el estado de la cuenta
            cursor.execute("""
                UPDATE cuentas
                SET descripcion = %s, estado = %s
                WHERE codigo = %s;
            """, (descripcion, estado, codigo))

            # Añadir una notificación de edición
            mensaje = f"Se ha editado la cuenta: {descripcion} (Código: {codigo})"
            url = "/cuentas"
            cursor.execute("""
                INSERT INTO notificaciones (mensaje, url, leido)
                VALUES (%s, %s, FALSE);
            """, (mensaje, url))

            conexion.commit()

        return jsonify({
            'message': 'Cuenta actualizada exitosamente',
            'cuenta': {
                'codigo': codigo,
                'descripcion': descripcion,
                'estado': estado
            }
        }), 200
    except Exception as e:
        conexion.rollback()
        return jsonify({'error': f'Error al actualizar la cuenta: {str(e)}'}), 500
    finally:
        conexion.close()

def dar_baja_cuenta():
    data = request.get_json()
    codigo = data.get('codigo')  # Código único de la cuenta
    estado = data.get('estado')  # true para activo, false para inactivo

    if not codigo:
        return jsonify({'error': 'Código de cuenta es obligatorio'}), 400

    # Conexión a la base de datos
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Verificar si la cuenta existe
            cursor.execute("SELECT cuenta_id FROM cuentas WHERE codigo = %s;", (codigo,))
            cuenta_existente = cursor.fetchone()

            if not cuenta_existente:
                return jsonify({'error': 'La cuenta no existe.'}), 404

            # Actualizar el estado de la cuenta
            cursor.execute("""
                UPDATE cuentas
                SET estado = %s
                WHERE codigo = %s;
            """, (estado, codigo))

            # Añadir una notificación de baja o alta
            accion = "dada de baja" if estado == 'false' else "reactivada"
            mensaje = f"La cuenta con código {codigo} ha sido {accion}."
            url = "/cuentas"
            cursor.execute("""
                INSERT INTO notificaciones (mensaje, url, leido)
                VALUES (%s, %s, FALSE);
            """, (mensaje, url))

            conexion.commit()

        return jsonify({
            'message': f'Cuenta {accion} exitosamente.',
            'cuenta': {
                'codigo': codigo,
                'estado': estado
            }
        }), 200
    except Exception as e:
        conexion.rollback()
        return jsonify({'error': f'Error al actualizar el estado de la cuenta: {str(e)}'}), 500
    finally:
        conexion.close()

def eliminar_notificacion(notificacion_id):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                DELETE FROM notificaciones WHERE id = %s;
            """, (notificacion_id,))
            conexion.commit()
        return jsonify({'message': 'Notificación eliminada exitosamente'}), 200
    except Exception as e:
        conexion.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close()



def contar_notificaciones_no_leidas():
    conexion = obtener_conexion()
    total_no_leidas = 0
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) FROM notificaciones WHERE leido = FALSE;
        """)
        total_no_leidas = cursor.fetchone()[0]
    conexion.close()
    return total_no_leidas


def obtener_todas_notificaciones():
    conexion = obtener_conexion()
    notificaciones = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT id, mensaje, url, leido
            FROM notificaciones
            ORDER BY creado_en DESC;
        """)
        notificaciones = cursor.fetchall()
    
    conexion.close()

    notificaciones_json = [
        {'id': n[0], 'mensaje': n[1], 'url': n[2], 'leido': n[3]} for n in notificaciones
    ]
    return jsonify({'notificaciones': notificaciones_json})



def marcar_notificaciones_leidas():
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE notificaciones
                SET leido = TRUE
                WHERE leido = FALSE;
            """)
            conexion.commit()

        return jsonify({'message': 'Notificaciones marcadas como leídas'}), 200
    except Exception as e:
        conexion.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close()

def obtener_cuentas_con_nivel():
    conexion = obtener_conexion()
    cuentas = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            WITH cuenta_jerarquia AS (
                SELECT 
                    c1.cuenta_id AS id_cuenta,
                    c1.codigo AS codigo_cuenta,
                    c1.descripcion AS descripcion_cuenta,
                    c1.cuenta_padre AS cuenta_padre,
                    c1.estado AS estado_cuenta,
                    c1.categoria AS categoria_cuenta,
                    c1.nivel AS nivel_cuenta,
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
                estado_cuenta,
                categoria_cuenta,
                nivel_cuenta,
                tiene_subcuentas
            FROM cuenta_jerarquia
            ORDER BY codigo_cuenta;
        """)
        cuentas = cursor.fetchall()
    conexion.close()
    return cuentas

def exportar_todas_cuentas_pdf():
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT codigo, descripcion, nivel
            FROM cuentas
            ORDER BY codigo
        """)
        cuentas = cursor.fetchall()

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elementos = []

        titulo = Paragraph("Cuentas Contables", styles['Title'])
        elementos.append(titulo)
        elementos.append(Spacer(1, 12))

        data = [["Código", "Descripción"]]
        for cuenta in cuentas:
            codigo = cuenta[0]
            descripcion = cuenta[1]
            nivel = cuenta[2] or 0  # Asegurarse de que el nivel no sea None
            indent = nivel * 15  # Ajusta el valor de indentación según tus necesidades
            # Crear un estilo de párrafo con indentación
            estilo_parrafo = ParagraphStyle(
                name='Indent{}'.format(nivel),
                parent=styles['Normal'],
                leftIndent=indent
            )
            descripcion_para = Paragraph(descripcion, estilo_parrafo)
            data.append([codigo, descripcion_para])

        tabla = Table(data, colWidths=[100, 400])
        tabla.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elementos.append(tabla)

        doc.build(elementos)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name="Cuentas_Contables.pdf",
            mimetype="application/pdf"
        )
    except Exception as e:
        print(f"Error al generar el PDF de las cuentas: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conexion:
            cursor.close()
            conexion.close()