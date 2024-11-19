from flask import Flask, render_template, request, redirect, make_response, flash, g, jsonify, url_for
import os
import hashlib
from flask_jwt_extended import JWTManager, create_access_token
import controladores.controlador_usuarios as controlador_usuarios
import controladores.controlador_ventas as controlador_ventas
import clases.clase_usuario as clase_usuario
import controladores.controlador_plantillas as controlador_plantillas
from bd_conexion import obtener_conexion  # Asegúrate de que la conexión a la base de datos esté configurada correctamente
from controladores.controlador_cuentas import obtener_todas_cuentas, obtener_cuentas_por_categoria_endpoint, añadir_cuenta,obtener_todas_notificaciones,marcar_notificaciones_leidas,eliminar_notificacion,contar_notificaciones_no_leidas
from werkzeug.utils import secure_filename
import datetime

# Directorio donde se guardarán las imágenes de perfil
UPLOAD_FOLDER = 'static/img/perfiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'super-secret'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
#app.run(ssl_context=('cert.pem', 'key.pem'))

# Verificar si el archivo es una imagen permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/subir_imagen_perfil", methods=["POST"])
def subir_imagen_perfil():
    # Verificar si el archivo ha sido enviado en la solicitud
    if 'imagen_perfil' not in request.files:
        flash('No se ha seleccionado ningún archivo.')
        return redirect(url_for('perfil_usuario'))

    file = request.files['imagen_perfil']

    # Verificar si no se ha seleccionado ningún archivo
    if file.filename == '':
        flash('No se seleccionó ningún archivo.')
        return redirect(url_for('perfil_usuario'))

    # Verificar si el archivo tiene un formato permitido
    if file and allowed_file(file.filename):
        # Aseguramos que el nombre del archivo sea seguro
        filename = secure_filename(file.filename)
        # Guardamos el archivo en el directorio de imágenes de perfiles
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Actualizar la tabla personas con la imagen
        dni = request.cookies.get('dni')
        controlador_usuarios.actualizar_imagen_perfil(dni, filename)

        flash('Imagen de perfil actualizada con éxito.')
        return redirect(url_for('perfil_usuario'))

    # Si el tipo de archivo no es permitido
    flash('Tipo de archivo no permitido. Selecciona una imagen válida (png, jpg, jpeg, gif).')
    return redirect(url_for('perfil_usuario'))

def obtener_descripcion_rol(rol):
    descripciones = {
        "Coordinador general": "Responsable de supervisar y organizar el equipo para cumplir objetivos, asegurando una comunicación efectiva y la resolución de problemas. Facilita la toma de decisiones, gestiona riesgos y mantiene informadas a las partes interesadas sobre el progreso del proyecto.",
        "Administrador de base de datos": "Responsable del diseño, implementación, seguridad y mantenimiento de la base de datos. Debe tener experiencia en la optimización del rendimiento de consultas y asegurar la integridad de los datos, con un enfoque en la resolución de problemas y la gestión eficiente de los datos.",
        "Analista": "Encargado de recopilar y analizar los requisitos del sistema. Debe ser capaz de identificar las necesidades del cliente y traducirlas en especificaciones técnicas claras para el equipo. Fuerte capacidad de análisis y comunicación efectiva son clave.",
        "Diseñador": "Encargado de la creación del diseño visual y de la experiencia del usuario (UI/UX). Debe ser capaz de crear interfaces atractivas y funcionales, asegurando que el sistema sea intuitivo y fácil de usar para los usuarios finales.",
        "Arquitecto de software": "Responsable de diseñar la estructura técnica del sistema, seleccionando tecnologías y definiendo los componentes clave. Debe tener una visión amplia del sistema y asegurarse de que el software cumpla con los requisitos de escalabilidad, seguridad y eficiencia.",
        "Programador": "Encargados de la codificación del sistema siguiendo las especificaciones del analista y el diseño del arquitecto. Deben tener experiencia en lenguajes de programación adecuados y ser capaces de trabajar en equipo, respetando plazos y estándares de calidad.",
        "Supervisor de calidad": "Responsable de asegurar que el sistema cumpla con los estándares de calidad definidos. Debe gestionar las pruebas y asegurar que se mantengan altos niveles de rendimiento, usabilidad y seguridad, monitoreando el progreso y haciendo ajustes si es necesario.",
        "Tester": "Encargados de realizar pruebas funcionales y de rendimiento del sistema para identificar errores y áreas de mejora. Deben tener habilidades técnicas para diseñar casos de prueba efectivos y capacidad para detectar problemas antes del despliegue del sistema.",
        "Capacitador": "Responsable de desarrollar y ejecutar planes de capacitación para los usuarios finales. Debe ser capaz de crear manuales y ofrecer formación clara y efectiva, asegurándose de que los usuarios puedan manejar el sistema correctamente.",
        "Asesor": "Ofrece asesoramiento especializado en áreas clave del proyecto, como estrategias de negocio, tecnología o gestión, y guía al equipo en la toma de decisiones críticas para el éxito del proyecto."
    }
    return descripciones.get(rol, "Rol no identificado")

# Ruta para eliminar la imagen de perfil
@app.route("/eliminar_imagen_perfil", methods=["POST"])
def eliminar_imagen_perfil():
    dni = request.cookies.get('dni')
    
    # Verificar si el usuario tiene una imagen
    imagen_actual = controlador_usuarios.obtener_imagen_perfil(dni)
    
    if not imagen_actual:
        flash('No tienes una imagen de perfil para eliminar.')
        return redirect(url_for('perfil_usuario'))

    # Eliminar la imagen del servidor
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], imagen_actual)):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], imagen_actual))

    # Eliminar la referencia de la imagen en la base de datos
    controlador_usuarios.eliminar_imagen_perfil(dni)

    flash('Imagen de perfil eliminada con éxito.')
    return redirect(url_for('perfil_usuario'))


# Inicializa JWTManager
jwt = JWTManager(app)
from functools import wraps

# Decorador para verificar el login en las rutas protegidas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not validar_token():  # Llama a la función que valida el token
            flash("Debe iniciar sesión para acceder a esta página.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def validar_token():
    token = request.cookies.get('token')
    dni = request.cookies.get('dni')
    usuario = controlador_usuarios.obtener_usuario(dni)
    if usuario and token == usuario[3]:
        return True
    return False


@app.route("/")
@app.route("/login_user")
def login():
    token = request.cookies.get('token')
    if not token:
        return render_template("login_user.html")
    if validar_token():
        return redirect("/index")
    return render_template("login_user.html")

@app.route("/index")
@login_required
def index():
    token = request.cookies.get('token')
    dni = request.cookies.get('dni')
    usuario = controlador_usuarios.obtener_usuario(dni)
    
    if usuario and (not usuario[6] or usuario[6] is None):
        usuario = list(usuario)  
        usuario[6] = "perfil_defecto.png" 

    breadcrumbs = [{'name': 'Inicio', 'url': '/index'}]
    return render_template("index.html", breadcrumbs=breadcrumbs, usuario=usuario)

@app.route("/actualizar_perfil", methods=["POST"])
def actualizar_perfil():
    dni = request.cookies.get('dni')
    nombres = request.form['nombres']
    apellidos = request.form['apellidos']
    
    # Actualiza los datos
    controlador_usuarios.actualizar_perfil_usuario(dni, nombres, apellidos)
    
    flash("Perfil actualizado correctamente.")
    return redirect(url_for('perfil_usuario'))



@app.route("/libro_diario", methods=["GET"])
@login_required
def libro_diario():
    token = request.cookies.get('token')
    dni = request.cookies.get('dni')
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
@login_required
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
def libro_mayor():
    token = request.cookies.get('token')
    dni = request.cookies.get('dni')
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
def libro_mayor_datos():
    periodo = request.args.get('periodo', '')
    cuenta = request.args.get('cuenta', '')

    # Verifica que se proporcione un período y una cuenta
    if not periodo or not cuenta:
        return jsonify({"movimientos": [], "total_debe": 0, "total_haber": 0})

    # Extrae año y mes del período
    año, mes = periodo.split('-')
    movimientos = controlador_plantillas.obtener_libro_mayor(mes, año, cuenta)

    # Calcula los totales de debe y haber
    total_deudor = sum(movimiento['deudor'] or 0 for movimiento in movimientos)
    total_acreedor = sum(movimiento['acreedor'] or 0 for movimiento in movimientos)

    # Formatea los movimientos para la respuesta JSON
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

@app.route("/libro_caja", methods=["GET"])
def libro_caja():
    token = request.cookies.get('token')
    dni = request.cookies.get('dni')
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

    return render_template(
        "libro_caja.html",
        movimientos=movimientos,
        breadcrumbs=breadcrumbs,
        usuario=usuario,
        total_deudor=total_deudor,
        total_acreedor=total_acreedor
    )



@app.route("/registro_ventas", methods=["GET"])
def registro_ventas():
    token = request.cookies.get('token')
    dni = request.cookies.get('dni')
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
def asientos_contables():
    token = request.cookies.get('token')
    dni = request.cookies.get('dni')
    usuario = controlador_usuarios.obtener_usuario(dni)

    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Asientos contables', 'url': '/asientos_contables'}
    ]
    movimientos = []

    return render_template("asientos_contables.html", movimientos=movimientos, breadcrumbs=breadcrumbs, usuario=usuario)


@app.route("/registro_compras", methods=["GET"])
def registro_compras():
    token = request.cookies.get('token')
    dni = request.cookies.get('dni')
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
def productos():
    token = request.cookies.get('token')
    dni = request.cookies.get('dni')
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
        password = request.form["password"].strip()  # Elimina espacios en blanco adicionales
        print(f"Intentando iniciar sesión con DNI: {dni}")
        
        # Obtenemos el usuario
        usuario = controlador_usuarios.obtener_usuario(dni)
        if not usuario:
            print("Usuario no encontrado")
            flash("Usuario no encontrado.")
            return redirect("/login_user")

        # Encriptamos la contraseña ingresada por el usuario
        h = hashlib.new("sha256")
        h.update(password.encode('utf-8'))  # Asegúrate de codificar la contraseña
        encpass = h.hexdigest().lower()  # Convertimos el hash a minúsculas para la comparación
        print(f"Contraseña encriptada ingresada: {encpass}, Contraseña esperada: {usuario[2]}")

        # Comparamos el hash de la contraseña ingresada con el hash almacenado
        if encpass == usuario[2].lower():  # Convertimos ambos a minúsculas para evitar problemas de mayúsculas/minúsculas
            access_token = create_access_token(identity=dni)
            controlador_usuarios.actualizartoken_usuario(dni, access_token)  # Actualiza el token en la base de datos
            resp = make_response(redirect("/index"))  # Cambiado para redirigir a index.html
            resp.set_cookie('token', access_token)
            resp.set_cookie('dni', dni)
            print("Inicio de sesión exitoso")
            return resp

        else:
            print("Contraseña incorrecta")
            flash("Contraseña incorrecta.")
            return redirect("/login_user")

    except Exception as e:
        print(f"Error en el inicio de sesión: {e}")
        flash("Ocurrió un error. Por favor, inténtelo de nuevo.")
        return redirect("/login_user")


@app.route("/procesar_logout")
def procesar_logout():
    try:
        dni = request.cookies.get('dni')
        controlador_usuarios.actualizartoken_usuario(dni, "")  # Borra el token en la base de datos
        resp = make_response(redirect("/login_user"))
        resp.set_cookie('token', '', 0)
        resp.set_cookie('dni', '', 0)
        print("Sesión cerrada correctamente")
        return resp
    except Exception as e:
        print(f"Error al cerrar sesión: {e}")
        flash("Error al cerrar la sesión.")
        return redirect("/login_user")


@app.route("/cuentas")
def cuentas():
    cuentas_data = obtener_todas_cuentas()  # Llama a la función para obtener los datos de las cuentas
    token = request.cookies.get('token')
    dni = request.cookies.get('dni')
    usuario = controlador_usuarios.obtener_usuario(dni)  # Obtener el usuario con DNI desde la base de datos

    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Cuentas contables', 'url': '/cuentas'}
    ]
    return render_template("cuentas.html", cuentas=cuentas_data, breadcrumbs=breadcrumbs, usuario=usuario)  # Pasar el usuario a la plantilla

@app.route("/ventas_contables")
def ventas_contables():
    ventas_data = controlador_ventas.obtener_todas_ventas()
    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Ventas contables', 'url': '/ventas_contables'}
    ]
    return render_template("ventas/ventas_contables.html", ventas=ventas_data, breadcrumbs=breadcrumbs)

@app.route("/boletas_ventas")
def boletas_ventas():
    boletas_data = controlador_ventas.obtener_boletas()
    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Boletas', 'url': '/boletas_ventas'}
    ]
    return render_template("ventas/boletas_ventas.html", boletas=boletas_data, breadcrumbs=breadcrumbs)
    
#@app.before_request
#def cargar_usuario():
#   token = request.cookies.get('token')
 #   dni = request.cookies.get('dni')
 #   if dni:
  #      g.usuario = controlador_usuarios.obtener_usuario(dni)  # Almacena el usuario en g
   # else:
    #    g.usuario = None  # Si no hay dni, asegura que g.usuario sea None


#@app.context_processor
#def contexto_global():
 #   return {'usuario': getattr(g, 'usuario', None)}  # Devuelve el usuario o None si no está definido

# Endpoint para obtener cuentas por categoría
@app.route("/cuentas/por_categoria", methods=["POST"])
def cuentas_por_categoria():
    return obtener_cuentas_por_categoria_endpoint()

# Nueva ruta para añadir una cuenta
@app.route("/cuentas/añadir", methods=["POST"])
def cuentas_añadir():
    try:
        # Llamar a la función para añadir una cuenta desde el controlador
        return añadir_cuenta()
    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500

########### PLANTILLAS ###########

#registro ventas
@app.route('/exportar-registro-ventas', methods=['GET'])
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
def obtener_notificaciones_endpoint():
    notificaciones = obtener_todas_notificaciones()
    total_no_leidas = contar_notificaciones_no_leidas()
    
    return jsonify({
        'notificaciones': notificaciones.json['notificaciones'],
        'total_no_leidas': total_no_leidas
    })


# Ruta para contar notificaciones no leídas
@app.route('/notificaciones/contar', methods=['GET'])
def contar_notificaciones_endpoint():
    total_no_leidas = contar_notificaciones_no_leidas()
    return jsonify({'total_no_leidas': total_no_leidas})

# Ruta para eliminar una notificación específica
@app.route('/notificaciones/eliminar', methods=['POST'])
def eliminar_notificacion_endpoint():
    data = request.get_json()
    notificacion_id = data.get('id')

    if not notificacion_id:
        return jsonify({'error': 'ID de notificación no proporcionado'}), 400

    return eliminar_notificacion(notificacion_id)

# Ruta para marcar todas las notificaciones como leídas
@app.route('/notificaciones/marcar_leidas', methods=['POST'])
def marcar_notificaciones_leidas_endpoint():
    return marcar_notificaciones_leidas()

@app.route("/perfil_usuario")
def perfil_usuario():
    token = request.cookies.get('token')
    dni = request.cookies.get('dni')

    if not token or not validar_token():
        return redirect("/login_user")
    
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
    
    return render_template("perfil_usuario.html", usuario=usuario, perfil=perfil, descripcion_rol=descripcion_rol, breadcrumbs=breadcrumbs)

# Iniciar el servidor
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)