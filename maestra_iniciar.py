from flask import Flask, render_template, request, redirect, make_response, flash, g, jsonify, url_for
import os
import hashlib
from flask_jwt_extended import JWTManager, create_access_token
import controladores.controlador_usuarios as controlador_usuarios
import controladores.controlador_ventas as controlador_ventas
import clases.clase_usuario as clase_usuario
from bd_conexion import obtener_conexion  # Asegúrate de que la conexión a la base de datos esté configurada correctamente
from controladores.controlador_cuentas import obtener_todas_cuentas, obtener_cuentas_por_categoria_endpoint, añadir_cuenta
from werkzeug.utils import secure_filename

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




# ... tus importaciones ...

# Diccionario de descripciones de roles
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
    "Asesor": "Ofrece asesoramiento especializado en áreas clave del proyecto, como estrategias de negocio, tecnología o gestión, y guía al equipo en la toma de decisiones críticas para el éxito del proyecto.",
    "Administrador del negocio": "Administrador del negocio"
}

def obtener_descripcion_rol(rol):
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
    
    if usuario and (not usuario[6] or usuario[6] is None):
        usuario = list(usuario)  
        usuario[6] = "perfil_defecto.png" 

    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'}
    ]
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

@app.route("/registro_ventas")
def registro_ventas():
    token = request.cookies.get('token')
    dni = request.cookies.get('dni')
    usuario = controlador_usuarios.obtener_usuario(dni)

    breadcrumbs = [
        {'name': 'Inicio', 'url': '/index'},
        {'name': 'Registro ventas', 'url': '/registro_ventas'}
    ]
    movimientos = []

    return render_template("registro_ventas.html", movimientos=movimientos, breadcrumbs=breadcrumbs, usuario=usuario)

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



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)

