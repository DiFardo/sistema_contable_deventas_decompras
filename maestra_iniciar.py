from flask import Flask, render_template, request, redirect, make_response, flash
import hashlib
from flask_jwt_extended import JWTManager, create_access_token
import controladores.controlador_usuarios as controlador_usuarios
from bd_conexion import obtener_conexion
from controladores.controlador_cuentas import obtener_todas_cuentas

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

@app.route("/ventas/productos")
def productos():
    token = request.cookies.get('token')
    dni = request.cookies.get('dni')
    usuario = controlador_usuarios.obtener_usuario(dni)

    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Productos', 'url': '/ventas/productos'}
    ]
    return render_template("Ventas/productos.html", breadcrumbs=breadcrumbs, usuario=usuario)


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



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)

