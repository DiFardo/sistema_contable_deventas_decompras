from flask import Flask, render_template, request, redirect, make_response, flash, g, jsonify
import hashlib
from flask_jwt_extended import JWTManager, create_access_token
import controladores.controlador_usuarios as controlador_usuarios
import controladores.controlador_ventas as controlador_ventas
import clases.clase_usuario as clase_usuario
import controladores.controlador_plantillas as controlador_plantillas
from bd_conexion import obtener_conexion  # Asegúrate de que la conexión a la base de datos esté configurada correctamente
from controladores.controlador_cuentas import obtener_todas_cuentas, obtener_cuentas_por_categoria_endpoint, añadir_cuenta

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
#app.run(ssl_context=('cert.pem', 'key.pem'))

# Inicializa JWTManager
jwt = JWTManager(app)


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
def index():
    token = request.cookies.get('token')
    dni = request.cookies.get('dni')
    usuario = controlador_usuarios.obtener_usuario(dni)

    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'}
    ]
    return render_template("index.html", breadcrumbs=breadcrumbs, usuario=usuario)

@app.route("/libro_caja")
def libro_caja():
    token = request.cookies.get('token')
    dni = request.cookies.get('dni')
    usuario = controlador_usuarios.obtener_usuario(dni)
    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Libro Caja y Bancos', 'url': '/libro_caja'}
    ]
    movimientos = []
    return render_template("libro_caja.html", movimientos=movimientos, breadcrumbs=breadcrumbs, usuario=usuario)

@app.route("/libro_diario")
def libro_diario():
    token = request.cookies.get('token')
    dni = request.cookies.get('dni')
    usuario = controlador_usuarios.obtener_usuario(dni)

    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Libro Diario', 'url': '/libro_diario'}
    ]
    movimientos = []

    return render_template("libro_diario.html", movimientos=movimientos, breadcrumbs=breadcrumbs, usuario=usuario)


@app.route("/libro_mayor")
def libro_mayor():
    token = request.cookies.get('token')
    dni = request.cookies.get('dni')
    usuario = controlador_usuarios.obtener_usuario(dni)

    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Libro Mayor', 'url': '/libro_mayor'}
    ]
    movimientos = []

    return render_template("libro_mayor.html", movimientos=movimientos, breadcrumbs=breadcrumbs, usuario=usuario)

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

@app.route("/registro_compras")
def registro_compras():
    token = request.cookies.get('token')
    dni = request.cookies.get('dni')
    usuario = controlador_usuarios.obtener_usuario(dni)

    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Registro compras', 'url': '/registro_compras'}
    ]
    movimientos = []

    return render_template("registro_compras.html", movimientos=movimientos, breadcrumbs=breadcrumbs, usuario=usuario)


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
        password = request.form["password"]
        print(f"Intentando iniciar sesión con DNI: {dni}")
        usuario = controlador_usuarios.obtener_usuario(dni)
        if not usuario:
            print("Usuario no encontrado")
            flash("Usuario no encontrado.")
            return redirect("/login_user")

        h = hashlib.new("sha256")
        h.update(bytes(password, encoding="utf-8"))
        encpass = h.hexdigest()
        print(f"Contraseña encriptada ingresada: {encpass}, Contraseña esperada: {usuario[2]}")

        if encpass == usuario[2]:  # Compara con el campo pass
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

# Iniciar el servidor
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)