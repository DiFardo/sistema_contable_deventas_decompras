from flask import Flask, render_template, request, redirect, make_response, flash, jsonify, url_for, send_file, g
import os
import hashlib
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity, set_access_cookies, unset_jwt_cookies,
    verify_jwt_in_request
)
import controladores.controlador_usuarios as controlador_usuarios
import controladores.controlador_ventas as controlador_ventas
import controladores.controlador_plantillas as controlador_plantillas
from bd_conexion import obtener_conexion
from controladores.controlador_cuentas import (
    obtener_todas_cuentas, obtener_cuentas_por_categoria_endpoint,
    añadir_cuenta, obtener_todas_notificaciones, marcar_notificaciones_leidas,
    eliminar_notificacion, contar_notificaciones_no_leidas
)
from werkzeug.utils import secure_filename
import datetime
from io import BytesIO
from datetime import timedelta

# Directorio donde se guardarán las imágenes de perfil
UPLOAD_FOLDER = 'static/img/perfiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuración de la clave secreta y JWT
app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Clave secreta para JWT
app.config['JWT_TOKEN_LOCATION'] = ['cookies']  # Almacenaremos el JWT en cookies
app.config['JWT_COOKIE_SECURE'] = True  # Las cookies solo se enviarán a través de HTTPS
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'  # Política SameSite para las cookies
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Desactivar protección CSRF para simplificar (puedes activarla si lo deseas)
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'  # Ruta de la cookie
app.config['JWT_SESSION_COOKIE'] = True  # La cookie expirará cuando se cierre el navegador
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=20)

# Inicializa JWTManager
jwt = JWTManager(app)

# Verificar si el archivo es una imagen permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta para subir imagen de perfil
@app.route("/subir_imagen_perfil", methods=["POST"])
@jwt_required()
def subir_imagen_perfil():
    if 'imagen_perfil' not in request.files:
        flash('No se ha seleccionado ningún archivo.')
        return redirect(url_for('perfil_usuario'))

    file = request.files['imagen_perfil']

    if file.filename == '':
        flash('No se seleccionó ningún archivo.')
        return redirect(url_for('perfil_usuario'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Obtener el DNI del usuario autenticado
        dni = get_jwt_identity()
        controlador_usuarios.actualizar_imagen_perfil(dni, filename)

        flash('Imagen de perfil actualizada con éxito.')
        return redirect(url_for('perfil_usuario'))

    flash('Tipo de archivo no permitido. Selecciona una imagen válida (png, jpg, jpeg, gif).')
    return redirect(url_for('perfil_usuario'))

def obtener_descripcion_rol(rol):
    descripciones = {
        # Tu diccionario de descripciones de roles
    }
    return descripciones.get(rol, "Rol no identificado")

# Ruta para eliminar la imagen de perfil
@app.route("/eliminar_imagen_perfil", methods=["POST"])
@jwt_required()
def eliminar_imagen_perfil():
    dni = get_jwt_identity()

    imagen_actual = controlador_usuarios.obtener_imagen_perfil(dni)

    if not imagen_actual:
        flash('No tienes una imagen de perfil para eliminar.')
        return redirect(url_for('perfil_usuario'))

    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], imagen_actual)):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], imagen_actual))

    controlador_usuarios.eliminar_imagen_perfil(dni)

    flash('Imagen de perfil eliminada con éxito.')
    return redirect(url_for('perfil_usuario'))

# Ruta de inicio de sesión
@app.route("/")
@app.route("/login_user")
def login():
    try:
        verify_jwt_in_request(optional=True)  # Verifica el token si existe
        if get_jwt_identity():  # Obtiene la identidad solo si el token es válido
            return redirect("/index")
    except Exception:
        pass  # Si no hay token o es inválido, continúa mostrando la página de login
    return render_template("login_user.html")

@app.route("/index")
@jwt_required()
def index():
    dni = get_jwt_identity()
    usuario = controlador_usuarios.obtener_usuario(dni)

    if usuario and (not usuario[6] or usuario[6] is None):
        usuario = list(usuario)
        usuario[6] = "perfil_defecto.png"

    breadcrumbs = [{'name': 'Inicio', 'url': '/index'}]
    return render_template("index.html", breadcrumbs=breadcrumbs, usuario=usuario)

@app.route("/actualizar_perfil", methods=["POST"])
@jwt_required()
def actualizar_perfil():
    dni = get_jwt_identity()
    nombres = request.form['nombres']
    apellidos = request.form['apellidos']

    controlador_usuarios.actualizar_perfil_usuario(dni, nombres, apellidos)

    flash("Perfil actualizado correctamente.")
    return redirect(url_for('perfil_usuario'))

# Añade @jwt_required() a las rutas que requieren autenticación
@app.route("/libro_diario", methods=["GET"])
@jwt_required()
def libro_diario():
    dni = get_jwt_identity()
    usuario = controlador_usuarios.obtener_usuario(dni)
    fecha = request.args.get("fecha", None)

    movimientos, total_debe, total_haber = (
        controlador_plantillas.obtener_libro_diario_por_fecha(fecha) if fecha else ([], 0, 0)
    )

    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Libro diario', 'url': '/libro_diario'}
    ]

    return render_template(
        "libro_diario.html",
        movimientos=movimientos,
        total_debe=total_debe,
        total_haber=total_haber,
        breadcrumbs=breadcrumbs,
        usuario=usuario
    )

@app.route("/libro_diario_datos")
@jwt_required()
def libro_diario_datos():
    fecha = request.args.get("fecha")
    movimientos, total_debe, total_haber = controlador_plantillas.obtener_libro_diario_por_fecha(fecha)
    
    filas = []
    for movimiento in movimientos:
        filas.append({
            "numero_correlativo": movimiento["numero_correlativo"],
            "fecha": movimiento["fecha"],
            "glosa": movimiento["glosa"],
            "codigo_del_libro": movimiento["codigo_del_libro"],
            "numero_correlativo_documento": movimiento["numero_correlativo_documento"],
            "numero_documento_sustentatorio": movimiento["numero_documento_sustentatorio"],
            "codigo_cuenta": movimiento["codigo_cuenta"],
            "denominacion": movimiento["denominacion"],
            "debe": movimiento["debe"],
            "haber": movimiento["haber"]
        })

    return jsonify(filas=filas, total_debe=total_debe, total_haber=total_haber)

@app.route("/libro_mayor")
@jwt_required()
def libro_mayor():
    dni = get_jwt_identity()
    usuario = controlador_usuarios.obtener_usuario(dni)
    cuentas = controlador_plantillas.obtener_cuentas_distintas()
    periodo = request.args.get('periodo', '')
    cuenta = request.args.get('cuenta', '')

    movimientos = []
    total_deudor = 0
    total_acreedor = 0

    if periodo and cuenta:
        año, mes = periodo.split('-')
        movimientos = controlador_plantillas.obtener_libro_mayor(mes, año, cuenta)
        
        for movimiento in movimientos:
            total_deudor += movimiento['deudor'] or 0
            total_acreedor += movimiento['acreedor'] or 0

    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Libro Mayor', 'url': '/libro_mayor'}
    ]

    return render_template(
        "libro_mayor.html", 
        movimientos=movimientos, 
        breadcrumbs=breadcrumbs, 
        usuario=usuario, 
        cuentas=cuentas,
        total_debe=total_deudor,
        total_haber=total_acreedor
    )

@app.route("/libro_mayor_datos", methods=["GET"])
@jwt_required()
def libro_mayor_datos():
    periodo = request.args.get('periodo', '')
    cuenta = request.args.get('cuenta', '')

    if not periodo or not cuenta:
        return jsonify({"movimientos": [], "total_debe": 0, "total_haber": 0})

    año, mes = periodo.split('-')
    movimientos = controlador_plantillas.obtener_libro_mayor(mes, año, cuenta)

    total_deudor = sum(movimiento['deudor'] or 0 for movimiento in movimientos)
    total_acreedor = sum(movimiento['acreedor'] or 0 for movimiento in movimientos)

    filas = []
    for movimiento in movimientos:
        filas.append({
            "fecha": movimiento["fecha"],
            "numero_correlativo": movimiento["numero_correlativo"],
            "glosa": movimiento["glosa"],
            "deudor": movimiento["deudor"],
            "acreedor": movimiento["acreedor"]
        })

    return jsonify({
        "movimientos": filas,
        "total_debe": total_deudor,
        "total_haber": total_acreedor   
    })

@app.route("/exportar-todas-las-cuentas", methods=["GET"])
@jwt_required()
def exportar_todas_las_cuentas():
    try:
        periodo = request.args.get('periodo', '')
        año, mes = periodo.split('-')
        output = controlador_plantillas.generar_excel_todas_las_cuentas(mes, año)
        
        nombre_archivo = f'libro_mayor_todas_cuentas_{año}_{mes}.xlsx'
        return send_file(
            output,
            download_name=nombre_archivo,
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        print(f"Error al exportar todas las cuentas: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/libro_caja", methods=["GET"])
@jwt_required()
def libro_caja():
    dni = get_jwt_identity()
    usuario = controlador_usuarios.obtener_usuario(dni)
    periodo = request.args.get("periodo", None)
    mes = año = None

    # Extraer mes y año si el periodo está presente
    if periodo:
        try:
            año, mes = periodo.split("-")
            # Verificar que mes y año son válidos
            if not (mes.isdigit() and año.isdigit()):
                raise ValueError("Invalid month or year format")
            print("Periodo extraído correctamente:", "Mes:", mes, "Año:", año)  # Mensaje de depuración
        except ValueError:
            mes = año = None
            print("Formato de periodo incorrecto")  # Mensaje de depuración
    
    # Llamar a la función obtener_libro_caja solo si mes y año están definidos
    if mes and año:
        movimientos, total_deudor, total_acreedor = controlador_plantillas.obtener_libro_caja(mes, año)
    else:
        movimientos, total_deudor, total_acreedor = [], 0, 0

    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Libro Caja y Bancos', 'url': '/libro_caja'}
    ]

    # Renderizar la plantilla con los datos obtenidos
    return render_template(
        "libro_caja.html",
        movimientos=movimientos,
        total_deudor=total_deudor,
        total_acreedor=total_acreedor,
        breadcrumbs=breadcrumbs,
        usuario=usuario
    )

@app.route("/registro_ventas", methods=["GET"])
@jwt_required()
def registro_ventas():
    dni = get_jwt_identity()
    usuario = controlador_usuarios.obtener_usuario(dni)
    periodo = request.args.get("periodo", None)
    mes = año = None
    if periodo:
        año, mes = periodo.split("-")
    registros, total_base_imponible, total_igv, total_total_comprobante = (
        controlador_plantillas.obtener_registro_ventas(mes, año) if mes and año else ([], 0, 0, 0)
    )
    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Registro ventas', 'url': '/registro_ventas'}
    ]
    return render_template(
        "registro_ventas.html",
        registros=registros,
        total_base_imponible=total_base_imponible,
        total_operacion_gravada=total_igv,
        total_total_comprobante=total_total_comprobante,
        breadcrumbs=breadcrumbs,
        usuario=usuario
    )

@app.route("/registro_ventas_datos", methods=["GET"])
@jwt_required()
def registro_ventas_datos():
    mes = request.args.get("month")
    anio = request.args.get("year")
    registros, total_base_imponible, total_igv, total_total_comprobante = controlador_plantillas.obtener_registro_ventas_por_fecha(mes, anio)
    
    filas = [
        {
            "correlativo": reg["correlativo"],
            "fecha_emision": reg["fecha_emision"],
            "tipo_comprobante": reg["tipo_comprobante"],
            "serie_comprobante": reg["serie_comprobante"],
            "numero_comprobante": reg["numero_comprobante"],
            "tipo_documento": reg["tipo_documento"],
            "numero_documento": reg["numero_documento"],
            "usuario": reg["usuario"],
            "base_imponible": reg["base_imponible"],
            "igv": reg["igv"],
            "total_comprobante": reg["total_comprobante"]
        }
        for reg in registros
    ]

    return jsonify(
        registros=filas,
        total_base_imponible=total_base_imponible,
        total_igv=total_igv,
        total_total_comprobante=total_total_comprobante
    )

@app.route("/registro_compras_datos", methods=["GET"])
@jwt_required()
def registro_compras_datos():
    mes = request.args.get("month")
    anio = request.args.get("year")
    registros, total_base_imponible, total_igv, total_total_comprobante = controlador_plantillas.obtener_registro_compras_por_fecha(mes, anio)
    
    filas = [
        {
            "correlativo": reg["correlativo"],
            "fecha_emision": reg["fecha_emision"],
            "tipo_comprobante": reg["tipo_comprobante"],
            "serie_comprobante": reg["serie_comprobante"],
            "numero_comprobante": reg["numero_comprobante"],
            "tipo_documento": reg["tipo_documento"],
            "numero_documento": reg["numero_documento"],
            "nombre_proveedor": reg["nombre_proveedor"],
            "base_imponible": reg["base_imponible"],
            "igv": reg["igv"],
            "total_comprobante": reg["total_comprobante"]
        }
        for reg in registros
    ]

    return jsonify(
        registros=filas,
        total_base_imponible=total_base_imponible,
        total_igv=total_igv,
        total_total_comprobante=total_total_comprobante
    )

@app.route('/exportar-libro-caja-bancos', methods=['GET'])
@jwt_required()
def exportar_libro_caja_bancos():
    periodo = request.args.get('periodo')
    if not periodo:
        return jsonify({'error': 'El parámetro "periodo" es requerido.'}), 400
    try:
        anio, mes = map(int, periodo.split('-'))
    except ValueError:
        return jsonify({'error': 'El formato del período es incorrecto. Debe ser "YYYY-MM".'}), 400
    return controlador_plantillas.generar_libro_caja_excel(mes, anio)

@app.route('/exportar-libro-diario', methods=['GET'])
@jwt_required()
def exportar_libro_diario():
    fecha = request.args.get('fecha')
    if not fecha:
        return jsonify({'error': 'El parámetro "fecha" es requerido.'}), 400
    try:
        datetime.datetime.strptime(fecha, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'El formato de la fecha es incorrecto. Debe ser "YYYY-MM-DD".'}), 400
    return controlador_plantillas.generar_libro_diario_excel(fecha)

@app.route("/asientos_contables")
@jwt_required()
def asientos_contables():
    dni = get_jwt_identity()
    usuario = controlador_usuarios.obtener_usuario(dni)

    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Asientos contables', 'url': '/asientos_contables'}
    ]
    movimientos = []

    return render_template("asientos_contables.html", movimientos=movimientos, breadcrumbs=breadcrumbs, usuario=usuario)


@app.route("/registro_compras", methods=["GET"])
@jwt_required()
def registro_compras():
    dni = get_jwt_identity()
    usuario = controlador_usuarios.obtener_usuario(dni)
    periodo = request.args.get("periodo", None)
    mes = año = None
    if periodo:
        año, mes = periodo.split("-")
    registros, total_base_imponible, total_igv, total_total_comprobante = (
        controlador_plantillas.obtener_registro_compras(mes, año) if mes and año else ([], 0, 0, 0)
    )
    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Registro compras', 'url': '/registro_compras'}
    ]
    return render_template(
        "registro_compras.html",
        registros=registros,
        total_base_imponible=total_base_imponible,
        total_operacion_gravada=total_igv,
        total_total_comprobante=total_total_comprobante,
        breadcrumbs=breadcrumbs,
        usuario=usuario
    )

@app.route("/ventas/productos")
@jwt_required()
def productos():
    dni = get_jwt_identity()
    usuario = controlador_usuarios.obtener_usuario(dni)
    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Productos', 'url': '/ventas/productos'}
    ]
    return render_template("ventas/productos.html", breadcrumbs=breadcrumbs, usuario=usuario)

# INICIAR SESION
@app.route("/procesar_login", methods=["POST"])
def procesar_login():
    try:
        dni = request.form["dni"]
        password = request.form["password"].strip()

        usuario = controlador_usuarios.obtener_usuario(dni)
        if not usuario:
            flash("Usuario no encontrado.")
            return redirect("/login_user")

        h = hashlib.new("sha256")
        h.update(password.encode('utf-8'))
        encpass = h.hexdigest().lower()

        if encpass == usuario[2].lower():
            access_token = create_access_token(identity=dni)
            resp = make_response(redirect("/index"))
            # Establecer el token en las cookies
            set_access_cookies(resp, access_token)
            return resp
        else:
            flash("Contraseña incorrecta.")
            return redirect("/login_user")

    except Exception as e:
        flash("Ocurrió un error. Por favor, inténtelo de nuevo.")
        return redirect("/login_user")

@app.route("/procesar_logout")
def procesar_logout():
    resp = make_response(redirect("/login_user"))
    # Eliminar las cookies JWT
    unset_jwt_cookies(resp)
    flash("Sesión cerrada correctamente.")
    return resp

@app.route("/cuentas")
@jwt_required()
def cuentas():
    cuentas_data = obtener_todas_cuentas()  # Llama a la función para obtener los datos de las cuentas
    dni = get_jwt_identity()
    usuario = controlador_usuarios.obtener_usuario(dni)  # Obtener el usuario con DNI desde la base de datos

    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Cuentas contables', 'url': '/cuentas'}
    ]
    return render_template("cuentas.html", cuentas=cuentas_data, breadcrumbs=breadcrumbs, usuario=usuario)  # Pasar el usuario a la plantilla

@app.route("/ventas_contables")
@jwt_required()
def ventas_contables():
    ventas_data = controlador_ventas.obtener_todas_ventas()
    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Ventas contables', 'url': '/ventas_contables'}
    ]
    return render_template("ventas/ventas_contables.html", ventas=ventas_data, breadcrumbs=breadcrumbs)
    
# Endpoint para obtener cuentas por categoría
@app.route("/cuentas/por_categoria", methods=["POST"])
@jwt_required()
def cuentas_por_categoria():
    return obtener_cuentas_por_categoria_endpoint()

# Nueva ruta para añadir una cuenta
@app.route("/cuentas/añadir", methods=["POST"])
@jwt_required()
def cuentas_añadir():
    try:
        # Llamar a la función para añadir una cuenta desde el controlador
        return añadir_cuenta()
    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500

########### PLANTILLAS ###########

#registro ventas
@app.route('/exportar-registro-ventas', methods=['GET'])
@jwt_required()
def exportar_registro_ventas():
    periodo = request.args.get('periodo')
    if not periodo:
        return jsonify({'error': 'El parámetro "periodo" es requerido.'}), 400
    try:
        anio, mes = map(int, periodo.split('-'))
    except ValueError:
        return jsonify({'error': 'El formato del período es incorrecto. Debe ser "YYYY-MM".'}), 400
    return controlador_plantillas.generar_registro_venta_excel(mes, anio)

@app.route('/exportar-registro-compras', methods=['GET'])
@jwt_required()
def exportar_registro_compras():
    periodo = request.args.get('periodo')
    if not periodo:
        return jsonify({'error': 'El parámetro "periodo" es requerido.'}), 400
    try:
        anio, mes = map(int, periodo.split('-'))
    except ValueError:
        return jsonify({'error': 'El formato del período es incorrecto. Debe ser "YYYY-MM".'}), 400
    return controlador_plantillas.generar_registro_compra_excel(mes, anio)

@app.route('/exportar-libro-mayor', methods=['GET'])
@jwt_required()
def exportar_libro_mayor():
    periodo = request.args.get('periodo')
    cuenta = request.args.get('cuenta')
    if not periodo or not cuenta:
        return jsonify({'error': 'Los parámetros "periodo" y "cuenta" son requeridos.'}), 400
    try:
        año, mes = periodo.split('-')
    except ValueError:
        return jsonify({'error': 'El formato del período es incorrecto. Debe ser "YYYY-MM".'}), 400

    return controlador_plantillas.generar_libro_mayor_excel(mes, año, cuenta)

@app.route('/notificaciones', methods=['GET'])
@jwt_required()
def obtener_notificaciones_endpoint():
    notificaciones = obtener_todas_notificaciones()
    total_no_leidas = contar_notificaciones_no_leidas()
    
    return jsonify({
        'notificaciones': notificaciones.json['notificaciones'],
        'total_no_leidas': total_no_leidas
    })


# Ruta para contar notificaciones no leídas
@app.route('/notificaciones/contar', methods=['GET'])
@jwt_required()
def contar_notificaciones_endpoint():
    total_no_leidas = contar_notificaciones_no_leidas()
    return jsonify({'total_no_leidas': total_no_leidas})

# Ruta para eliminar una notificación específica
@app.route('/notificaciones/eliminar', methods=['POST'])
@jwt_required()
def eliminar_notificacion_endpoint():
    data = request.get_json()
    notificacion_id = data.get('id')

    if not notificacion_id:
        return jsonify({'error': 'ID de notificación no proporcionado'}), 400

    return eliminar_notificacion(notificacion_id)

# Ruta para marcar todas las notificaciones como leídas
@app.route('/notificaciones/marcar_leidas', methods=['POST'])
@jwt_required()
def marcar_notificaciones_leidas_endpoint():
    return marcar_notificaciones_leidas()

@app.route("/perfil_usuario")
@jwt_required()
def perfil_usuario():
    # Obtener el DNI del usuario autenticado desde el token JWT
    dni = get_jwt_identity()

    # Obtener información del usuario
    usuario = controlador_usuarios.obtener_usuario(dni)
    perfil = controlador_usuarios.obtener_detalles_perfil(dni)

    if not perfil:
        flash("Usuario no encontrado.")
        return redirect("/index")

    # Obtener la descripción del rol
    descripcion_rol = obtener_descripcion_rol(perfil[3])

    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Perfil del Usuario', 'url': '/perfil_usuario'}
    ]

    return render_template(
        "perfil_usuario.html",
        usuario=usuario,
        perfil=perfil,
        descripcion_rol=descripcion_rol,
        breadcrumbs=breadcrumbs
    )

def cargar_usuario():
    if request.endpoint in app.view_functions and 'static' not in request.path:
        if get_jwt_identity():
            dni = get_jwt_identity()
            usuario = controlador_usuarios.obtener_usuario(dni)
            if usuario:
                g.usuario = usuario
            else:
                g.usuario = None
        else:
            g.usuario = None

@app.context_processor
def contexto_global():
    return {'usuario': getattr(g, 'usuario', None)}

@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, public, max-age=0"
    response.headers["Expires"] = "0"
    response.headers["Pragma"] = "no-cache"
    return response

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """
    Manejo específico de tokens expirados.
    """
    flash("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.")
    resp = make_response(redirect(url_for('login')))
    unset_jwt_cookies(resp)  # Elimina cookies vencidas
    return resp

# Manejador general de errores 401
@app.errorhandler(401)
def unauthorized_error_handler(e):
    """
    Manejo general de errores de autorización.
    """
    # Verificar si el error es por token expirado
    if "token has expired" in str(e):
        # Redirigir al flujo específico de expiración de tokens
        return expired_token_callback(None, None)

    # Caso general para otros errores de autorización
    flash("No autorizado. Por favor, inicia sesión.")
    resp = make_response(redirect(url_for('login')))
    unset_jwt_cookies(resp)  # Limpia cookies, por si acaso
    return resp

@jwt.unauthorized_loader
def custom_unauthorized_response(err_str):
    """
    Se llama cuando falta el token o es inválido.
    Redirige al usuario a la página de inicio de sesión.
    """
    # Redirigir al login si no hay token
    return redirect(url_for('login'))

@jwt.invalid_token_loader
def custom_invalid_token_response(err_str):
    """
    Se llama cuando el token es inválido.
    Redirige al usuario a la página de inicio de sesión.
    """
    # Redirigir al login si el token es inválido
    return redirect(url_for('login'))

def get_rutas():
    with app.app_context():
        return [
            {"nombre": "Inicio", "url": url_for('index')},
            {"nombre": "Login", "url": url_for('login')},
            {"nombre": "Perfil de Usuario", "url": url_for('perfil_usuario')},
            {"nombre": "Libro Diario", "url": url_for('libro_diario')},
            {"nombre": "Libro Mayor", "url": url_for('libro_mayor')},
            {"nombre": "Libro Caja y Bancos", "url": url_for('libro_caja')},
            {"nombre": "Registro de Ventas", "url": url_for('registro_ventas')},
            {"nombre": "Registro de Compras", "url": url_for('registro_compras')},
            {"nombre": "Productos", "url": url_for('productos')},
            {"nombre": "Cuentas Contables", "url": url_for('cuentas')},
            # Agrega más rutas aquí
        ]

@app.route('/buscar')
@jwt_required()
def buscar():
    dni = get_jwt_identity()
    usuario = controlador_usuarios.obtener_usuario(dni)
    term = request.args.get('term', '').lower()
    rutas = get_rutas()
    resultados = [ruta for ruta in rutas if term in ruta['nombre'].lower()]
    return render_template('buscar.html', term=term, resultados=resultados, usuario=usuario)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('page404.html'), 404

@app.route('/prueba1')
def prueba1():
    return render_template('prueba1.html')

# Iniciar el servidor
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)