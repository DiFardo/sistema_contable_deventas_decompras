from flask import Flask, render_template, request, redirect, make_response, flash, g
import hashlib
from flask_jwt_extended import JWTManager, create_access_token
import controladores.controlador_usuarios as controlador_usuarios
import controladores.controlador_ventas as controlador_ventas
import clases.clase_usuario as clase_usuario
from bd_conexion import obtener_conexion  # Asegúrate de que la conexión a la base de datos esté configurada correctamente
from controladores.controlador_cuentas import obtener_todas_cuentas  # Importa la función para obtener las cuentas

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

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


@app.route("/cuentas")
def cuentas():
    cuentas_data = obtener_todas_cuentas()
    token = request.cookies.get('token')
    dni = request.cookies.get('dni')
    usuario = controlador_usuarios.obtener_usuario(dni)

    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Cuentas contables', 'url': '/cuentas'}
    ]
    return render_template("cuentas.html", cuentas=cuentas_data, breadcrumbs=breadcrumbs, usuario=usuario)




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

from flask import g

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




# Iniciar el servidor
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)

