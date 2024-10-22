from flask import Flask, render_template, request, redirect, flash, jsonify, session, url_for, make_response
from flask_jwt import JWT, jwt_required, current_identity
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from calendar import monthrange
import hashlib
import os
import requests
import random
import logging
import controladores.controlador_producto as controlador_producto
import controladores.controlador_usuario as controlador_usuario
from hashlib import sha256

class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id

def authenticate(username, password):
    userfrombd = controlador_usuario.obtener_user_por_username(username)
    user = None
    if userfrombd is not None:
        user = User(userfrombd[0], userfrombd[1], userfrombd[2])
    if user is not None:
        hashed_password = sha256(password.encode('utf-8')).hexdigest()
        if (user.password == password) or (user.password == hashed_password):
            return user
    return None

def identity(payload):
    user_id = payload['identity']
    userfrombd = controlador_usuario.obtener_usuario_por_id_auth(user_id)
    user = None
    if userfrombd is not None:
        user = User(userfrombd[0], userfrombd[1], userfrombd[2])
    #return userid_table.get(user_id, None)
    return user

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

jwt = JWT(app, authenticate, identity)
app.secret_key = 'mysecretkey'

###### RUTAS USUARIO #####
###DECORADORES"""
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session.get('user_type') != 1:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@app.route('/index')
def index():
    if 'cart' not in session:
        session['cart'] = {}
    productos_novedades = controlador_producto.obtener_productos_mas_vendidos()
    return render_template('index.html', productos_novedades=productos_novedades)

@app.route('/mujer')
def mujer():
    productos = controlador_producto.obtener_productos_mujer()
    return render_template('mujer.html', productos=productos)

@app.route('/carro_compra')
def carro_compra():
    return render_template('carro_compra.html')

#@app.route('/acercade')
#def acercade():
#    return render_template('acerca_De.html')

@app.route('/contactos')
def contactos():
    return render_template('contactos.html')

@app.route('/hombre')
def hombre():
    productos = controlador_producto.obtener_productos_hombre()
    return render_template('hombre.html', productos=productos)

@app.route('/registrarse')
def registrarse():
    return render_template('registrarse.html')

###### LEGALES #####
@app.route('/base_legales')
def base_legales():
    return render_template('datos_legales/base_legales.html')

@app.route('/cambios_devoluciones')
def cambios_devoluciones():
    return render_template('datos_legales/cambios_devoluciones.html')

@app.route('/politica_privacidad')
def politica_privacidad():
    return render_template('datos_legales/politica_privacidad.html')

@app.route('/preguntas_frecuentes')
def preguntas_frecuentes():
    return render_template('datos_legales/preguntas_frecuentes.html')

@app.route('/terminos_condiciones')
def terminos_condiciones():
    return render_template('datos_legales/terminos_condiciones.html')

###### RUTAS ADMINISTRADOR #####
@app.route('/admin_inicio')
@admin_required
def admin_inicio():
    try:
        return render_template('/administrador/admin_home.html')
    except Exception as e:
        logging.error(f"Error en admin_inicio: {e}")
        flash('Error al cargar el dashboard del administrador.')
        return redirect(url_for('login'))

@app.route('/admin_user')
def admin_user():
    return render_template('administrador/botones_admini_user.html')
#Rutas para agregar, editar, actualizar, eliminar USUARIO

@app.route("/usuarios")
@admin_required
def usuarios():
    usuarios = controlador_usuario.obtener_usuarios()
    return render_template("administrador/usuarios.html", usuarios=usuarios)

@app.route("/agregar_usuario")
@admin_required
def formulario_agregar_usuario():
    tipos_usuario = controlador_usuario.obtener_nombre_tipo_usuario()
    # tipos_documento = controlador_usuario.obtener_nombre_tipo_documento()
    # print(tipos_documento)
    print(tipos_usuario)
    return render_template("administrador/agregar_usuario.html", tipos_usuario=tipos_usuario) #tipos_documento=tipos_documento

def fn_buscarDni(dni):
    dniBuscar = dni
    url_form = 'https://api.apis.net.pe/v2/reniec/dni?numero=' + dniBuscar
    token = "apis-token-8958.O758vEuKBUXkErNRgyLoM8dWrrkGJEOm"
    headers = {"Authorization": "Bearer " + token}
    try:
        response = requests.get(url_form, headers=headers )
        response.raise_for_status()  # Lanza una excepción para códigos de estado 4xx/5xx
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print("Error HTTP:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error de Conexión:", errc)
    except requests.exceptions.Timeout as errt:
        print("Error de Tiempo de Espera (Timeout):", errt)
    except requests.exceptions.RequestException as err:
        print("Error en la Solicitud API:", err)
    return {'error': 'Error al obtener los datos'}

@app.route('/agregar_dni')
@admin_required
def agregar_dni():
    return render_template('administrador/agregar_usuario_dni.html')

@app.route('/buscarDni', methods=['GET'])
@admin_required
def buscar_dni():
    dni = request.args.get('dni')
    if not dni:
        return jsonify({'error': 'No se proporcionó un DNI'}), 400
    usuario = fn_buscarDni(dni)
    if 'error' in usuario:
        return jsonify(usuario), 500
    return jsonify({
        'nombres': usuario.get('nombres', ''),
        'apellidoPaterno': usuario.get('apellidoPaterno', ''),
        'apellidoMaterno': usuario.get('apellidoMaterno', ''),
    })

@app.route("/guardar_usuario", methods=["POST"])
@admin_required
def guardar_usuario():
    #numeroDocumento= request.form["numeroDocumento"]
    nombre= request.form["nombres"]
    email = request.form["email"]
    telefono = request.form["telefono"]
    apellido = request.form["apellidos"]
    nombre_usuario = request.form["usuario"]
    contrasenia = request.form["contraseña"]
    fecha_nacimiento = request.form["fechaNacimiento"]
    tipo_usuario = request.form["id_TipoUsuario"]
    #tipo_documento = request.form["id_TipoDocumento"]
    controlador_usuario.insertar_usuario(nombre, email, telefono, apellido, nombre_usuario, contrasenia, fecha_nacimiento, tipo_usuario)
    # De cualquier modo, y si todo fue bien, redireccionar
    return redirect("/usuarios")

#Guardar Cliente:
@app.route("/guardar_cliente", methods=["POST"])
def guardar_cliente():
    #numeroDocumento= request.form["numeroDocumento"]
    nombre= request.form["nombres"]
    email = request.form["email"]
    telefono = request.form["telefono"]
    apellido = request.form["apellidos"]
    nombre_usuario = request.form["usuario"]
    contrasenia = request.form["contraseña"]
    fecha_nacimiento = None
    tipo_usuario = 2
    #tipo_documento = request.form["id_TipoDocumento"]
    controlador_usuario.insertar_usuario(nombre, email, telefono, apellido, nombre_usuario, contrasenia, fecha_nacimiento, tipo_usuario)
    # De cualquier modo, y si todo fue bien, redireccionar
    return redirect("/index")

@app.route("/eliminar_usuario", methods=["POST"])
@admin_required
def eliminar_usuario():
    controlador_usuario.eliminar_usuario(request.form["id"])
    return redirect("/usuarios")

@app.route("/formulario_editar_usuario/<int:id>")
@admin_required
def editar_usuario(id):
    # Obtener el usuario por ID
    tipos_usuario = controlador_usuario.obtener_nombre_tipo_usuario()
    #tipos_documento = controlador_usuario.obtener_nombre_tipo_documento()
    usuario = controlador_usuario.obtener_usuario_por_id(id)
    return render_template("administrador/editar_usuarios.html", usuario=usuario, tipos_usuario=tipos_usuario) #, tipos_documento=tipos_documento

@app.route("/actualizar_usuario", methods=["POST"])
@login_required
@admin_required
def actualizar_usuario():
    #numeroDocumento= request.form["numeroDocumento"]
    id = request.form["id"]
    nombre= request.form["nombres"]
    email = request.form["email"]
    telefono = request.form["telefono"]
    apellido = request.form["apellidos"]
    nombre_usuario = request.form["usuario"]
    contrasenia = request.form["contraseña"]
    fecha_nacimiento = request.form["fechaNacimiento"]
    #estado = request.form["status"]
    tipo_usuario = request.form["id_TipoUsuario"]
    #tipo_documento = request.form["id_TipoDocumento"]
    controlador_usuario.actualizar_usuario(nombre, email, telefono, apellido, nombre_usuario,contrasenia,fecha_nacimiento,tipo_usuario, id)
    return redirect("/usuarios")

@app.route('/verContactos/<int:id>')
@login_required
def verContactos(id):
    contactos = controlador_usuario.obtener_usuario_por_id(id)
    tarjetas = controlador_usuario.ver_tarjetas(id)
    return render_template('datos_personales/datos_personales.html', contactos=contactos, tar=tarjetas)

@app.route('/editarContactos_user/<int:id>', methods=['POST'])
@login_required
def editarContactos_user(id):
    nombre= request.form["nombre"]
    apellido = request.form["apellido"]
    email = request.form["email"]
    telefono = request.form["telefono"]
    fechaNacimiento = request.form["fechaNacimiento"]
    controlador_usuario.actualizar_usuario_por_usuario(nombre,apellido, email, telefono,  fechaNacimiento, id)
    return redirect(url_for('verContactos', id=id))

@app.route('/id_a_agregar_tarjeta')
@login_required
def id_a_agregar_tarjeta():
    return render_template('datos_personales/agregar_tarjeta.html')

#@app.route("/eliminar_tarjeta/<int:id>", methods=["POST"])
#def eliminar_tarjeta(id):
#    controlador_usuario.eliminar_tarjeta(id)
#    return redirect(url_for('verContactos', id=session['user_id']))

@app.route("/dar_de_baja_tarjeta/<int:id>", methods=["POST"])
def dar_de_baja_tarjeta(id):
    controlador_usuario.dar_de_baja_tarjeta(id)
    return redirect(url_for('verContactos', id=session['user_id']))

@app.route('/agregar_tarjetas', methods=['POST'])
@login_required
def agregar_tarjetas():
    numero_tarjeta = request.form['numero_tarjeta']
    nombre = request.form['titular']
    mes = int(request.form['mes'])
    año = int(request.form['year'])
    ultimo_dia = monthrange(año, mes)[1]
    fecha_vencimiento = f"{año}-{mes:02d}-{ultimo_dia}"
    cvv = request.form['codigo_seguridad']
    controlador_usuario.agregar_tarjeta(numero_tarjeta, nombre, fecha_vencimiento, cvv, session['user_id'])
    return redirect(url_for('verContactos', id=session['user_id']))

@app.route('/ir_a_pagos/<int:id>')
@login_required
def ir_a_pagos(id):
    sub = controlador_usuario.detalle_pedido(id)
    ped = controlador_usuario.pago_pedido(id)
    tarjeta = controlador_usuario.ver_tarjetas(session['user_id'])
    print(ped)
    return render_template('pago.html', sub = sub , ped = ped, tarjeta = tarjeta)

@app.route('/pagar_pedidos/<int:id>', methods=['POST'])
@login_required
def pagar_pedidos(id):
    total = request.form['total']
    id_tarjeta = request.form['tarjeta']
    try:
        controlador_usuario.insertar_pago(id, id_tarjeta, total)
        flash('Pago realizado con éxito', 'success')
        return redirect(url_for('ver_pendientes'))
    except Exception as e:
        flash(f'No se pudo realizar el pago: {str(e)}', 'danger')
    return redirect(url_for('ver_pendientes'))

@app.route('/cancelar_pedido/<int:id>', methods=['POST'])
@login_required
def cancelar_pedido(id):
    try:
        controlador_usuario.cancelar_pedido(id)
        flash('Pedido cancelado y stock restaurado', 'success')
    except Exception as e:
        flash(f'No se pudo cancelar el pedido: {str(e)}', 'danger')
    return redirect(url_for('ver_pendientes'))

#Rutas para agregar, editar, actualizar, eliminar PRODUCTO
@app.route("/productos")
@admin_required
def productos():
    productos = controlador_producto.obtener_producto()
    return render_template("administrador/producto.html", productos=productos)

@app.route("/agregar_producto")
@admin_required
def formulario_agregar_producto():
    categorias = controlador_producto.obtener_nombre_categoria()
    print(categorias)
    return render_template("administrador/agregar_producto.html", categorias=categorias)

@app.route("/guardar_producto", methods=["POST"])
def guardar_producto():
    imagen = request.files.get('imagenes')
    if imagen and imagen.filename:
        nombre_imagen = secure_filename(imagen.filename)
        ruta_destino = os.path.join(app.root_path, 'static', 'assets' ,'img', 'productos', nombre_imagen)
        imagen.save(ruta_destino)
        ruta_imagen_db = os.path.join('img', 'productos', nombre_imagen).replace('\\', '/')
    else:
        ruta_imagen_db = 'img/productos/default.jpg'
    nombreProducto = request.form.get("nombreProducto", "")
    descripcion = request.form.get("descripcion", "")
    precio = request.form.get("precio", "0")
    stock = request.form.get("stock", "activo") #¿Cómo que activo?
    id_Categoria = request.form.get("id_Categoria", "1")
    genero = request.form.get("genero", "")
    talla = request.form.get("talla", "")
    controlador_producto.insertar_producto(nombreProducto, descripcion, precio, stock, id_Categoria, ruta_imagen_db, talla, genero)
    return redirect(url_for('productos'))

@app.route("/actualizar_producto", methods=["POST"])
def actualizar_producto():
    id = request.form["id"]
    imagen = request.form["imagen"]
    nombreProducto= request.form["nombreProducto"]
    descripcion = request.form["descripcion"]
    precio = request.form["precio"]
    stock = request.form["stock"]
    id_Categoria = request.form["id_Categoria"]
    talla = request.form["talla"]
    controlador_producto.actualizar_producto(nombreProducto, descripcion, precio,stock,id_Categoria, imagen, talla, id)
    return redirect("/productos")

@app.route("/eliminar_producto", methods=["POST"])
def eliminar_producto():
    controlador_producto.eliminar_producto(request.form["id"])
    return redirect("/productos")

@app.route("/formulario_editar_producto/<int:id>")
@admin_required
def editar_producto(id):
    # Obtener el usuario por ID
    producto = controlador_producto.obtener_producto_por_id(id)
    tipos_categorias = controlador_producto.obtener_nombre_categoria()
    return render_template("administrador/editar_producto.html", producto=producto, tipos_categorias = tipos_categorias)

@app.route('/producto_detalle/<int:id>')
@login_required
def producto_detalle(id):
    producto = controlador_producto.obtener_producto_por_id(id)
    if not producto:
        flash('Producto no encontrado')
        return redirect('/productos')
    return render_template('producto_detalle.html', producto=producto)

#PRUEBAS CARRITO
@app.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():
    product_id = request.form.get('product_id')
    if product_id in session.get('cart', {}):
        del session['cart'][product_id]
        session.modified = True
    return redirect(url_for('show_cart'))

@app.route('/clear_cart', methods=['POST'])
@login_required
def clear_cart():
    session['cart'] = {}
    session.modified = True
    return redirect(url_for('show_cart'))

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form.get('product_id')
    cantidad = int(request.form.get('cantidad', 1))
    if 'cart' not in session:
        session['cart'] = {}
    producto = controlador_producto.obtener_producto_por_id(int(product_id))
    if producto:
        stock_disponible = producto[4]
        # Verificar si la cantidad solicitada no excede el stock disponible
        if cantidad > stock_disponible:
            return jsonify({'message': 'Cantidad solicitada excede el stock disponible', 'cart': session.get('cart', {})})
        if product_id in session['cart']:
            nueva_cantidad = session['cart'][product_id]['cantidad'] + cantidad
            if nueva_cantidad > stock_disponible:
                return jsonify({'message': 'Cantidad total excede el stock disponible', 'cart': session.get('cart', {})})
            session['cart'][product_id]['cantidad'] = nueva_cantidad
        else:
            session['cart'][product_id] = {
                'id': producto[0],
                'nombre': producto[1],
                'precio': float(producto[3]),
                'cantidad': cantidad
            }
        session.modified = True
        return jsonify({'message': 'Producto añadido al carrito', 'cart': session['cart']})
    else:
        return jsonify({'message': 'Producto no encontrado', 'cart': session.get('cart', {})})

@app.route('/cart')
@login_required
def show_cart():
    cart = session.get('cart', {})
    total = sum(float(item['precio']) * item['cantidad'] for item in cart.values()) if cart else 0
    return render_template('carrito-prueba.html', cart=cart, total=total)

@app.route('/guardar_detalles', methods=['POST'])
def guardar_detalle():
    id_producto = request.form.getlist('id_producto[]')
    cantidad = request.form.getlist('cantidad[]')
    id_user = request.form['id_user']
    if not id_producto or not cantidad or not id_user:
        return redirect(url_for('show_cart'))
    if not all(c.isdigit() and int(c) > 0 for c in cantidad):
        return redirect(url_for('show_cart'))
    pedido_id = controlador_producto.insertar_nuevo_pedido(id_user)
    for i in range(len(id_producto)):
        controlador_producto.guardar_detalle(id_producto[i], cantidad[i], pedido_id)
    session['cart'] = {}
    return redirect(url_for('ver_pendientes'))

@app.route('/ver_pendientes')
@login_required
def ver_pendientes():
    try:
        pedidos = controlador_usuario.ver_pedidos_pendientes(session['user_id'])
        return render_template('datos_personales/pedidos_pendiente.html', pedidos=pedidos)
    except Exception as e:
        flash(f'Error al cargar los pedidos pendientes: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/pagar_pedido/<int:id>')
@login_required
def pagar_pedido(id):
    controlador_usuario.pagar_pedido(id)
    return redirect(url_for('ver_pendientes'))

@app.route('/ver_historial')
@login_required
def ver_historial():
    try:
        pedidos = controlador_usuario.historial_pedido(session['user_id'])
        return render_template('historial_pedido.html', pedidos=pedidos)
    except Exception as e:
        flash(f'Error al cargar el historial de pedidos: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/ver_detalle_pedido/<int:id>')
@login_required
def ver_detalle_pedido(id):
    detalle = controlador_usuario.historial_detalle_pedido(id)
    print(detalle)
    return render_template('detalle_pedido.html', detalle=detalle)



#############COOKIES
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            usuario = request.form['usuario']
            contrasenia = request.form['contrasenia']
            user = controlador_usuario.login(usuario, contrasenia)
            if user:
                session['logged_in'] = True
                session['user_type'] = user[0][0]
                session['user_id'] = user[0][1]
                session['user_name'] = user[0][2]
                session['token'] = user[0][3]
                session['email'] = user[0][4]
                aleatorio = str(random.randint(1, 1024))
                token = hashlib.sha256(aleatorio.encode("utf-8")).hexdigest()
                logging.info(f"User type: {session['user_type']}")
                if session['user_type'] == 1:
                    response = make_response(redirect(url_for('admin_inicio')))
                else:
                    response = make_response(redirect(url_for('index')))
                response.set_cookie('email', session['email'])
                response.set_cookie('token', token)
                controlador_usuario.actualizar_token_usuario(usuario, token)
                flash('Login successful!')
                return response
            else:
                flash('Usuario o contraseña incorrectos')
                return redirect(url_for('index'))
        except ValueError as e:
            logging.error(f"Error en login (autenticación): {e}")
            flash('Usuario o contraseña incorrectos.')
            return redirect(url_for('index'))
        except Exception as e:
            logging.error(f"Error inesperado en login: {e}")
            flash('Error al procesar la solicitud.')
            return redirect(url_for('index'))
    else:
        return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente.')
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('token', "", expires=0)
    resp.set_cookie('email', "", expires=0)
    return resp

####CRUDS
@app.route('/admin_crud')
@admin_required
def admin_crud():
    return render_template('administrador/INT_CRUDS.html')

###TARJETA
@app.route('/admin_crud_tarjeta_general')
@admin_required
def admin_crud_tarjeta_general():
    usuarios = controlador_usuario.obtener_mantenimiento_tarjeta()
    return render_template('CRUDS/TARJETAS/general.html', usuarios=usuarios)

@app.route('/admin_crud_insertar_tarjeta')
@admin_required
def admin_crud_insertar_tarjeta():
    obo = controlador_usuario.obtener_usuarios()
    return render_template('CRUDS/TARJETAS/insert.html', obo=obo)

@app.route('/admin_crud_actualizar_tarjeta/<int:id>')
@admin_required
def admin_crud_actualizar_tarjeta(id):
    usuario = controlador_usuario.obtener_mantenimiento_tarjeta_x_id(id)
    return render_template('CRUDS/TARJETAS/actualizar.html', usuario=usuario)

@app.route('/admin_crud_actualizar_tarjeta_completa' , methods=['POST'])
@admin_required
def admin_crud_actualizar_tarjeta_completa():
    id = request.form["id"]
    nombre= request.form["nombres"]
    email = request.form["email"]
    telefono = request.form["telefono"]
    apellido = request.form["apellidos"]
    nombre_usuario = request.form["usuario"]
    id_usu = request.form["id_usu"]
    controlador_usuario.actualizar_tarjeta(email,telefono,apellido,nombre_usuario, id_usu ,id)
    return redirect("/admin_crud_tarjeta_general")

@app.route('/admin_crud_insert_tarjeta', methods=['POST'])
@admin_required
def admin_crud_insert_tarjeta():
    email = request.form["nombres"]
    telefono = request.form["apellidos"]
    apellido = request.form["email"]
    nombre_usuario = request.form["telefono"]
    usuario = request.form["usuario"]
    if controlador_usuario.agregar_tarjeta(email,telefono,apellido,nombre_usuario, usuario):
        flash('Tarjeta agregada correctamente')
        return redirect('/admin_crud_tarjeta_general')
    flash('Error al agregar la tarjeta')
    return redirect('/admin_crud_tarjeta_general')

@app.route('/admin_crud_eliminar_tarjeta', methods=['POST'])
@admin_required
def admin_crud_eliminar_tarjeta():
    controlador_usuario.eliminar_tarjeta(request.form["id"])
    return redirect("/admin_crud_tarjeta_general")

##DIRECCION
@app.route('/admin_crud_direccion_general')
@admin_required
def admin_crud_direccion_general():
    usuarios = controlador_usuario.obtener_direccion_mantenimiento()
    return render_template('CRUDS/DIRECCION/general.html', usuarios=usuarios)

@app.route('/admin_crud_insertar_direccion')
@admin_required
def admin_crud_insertar_direccion():
    obo = controlador_usuario.obtener_usuarios()
    return render_template('CRUDS/DIRECCION/insert.html', obo=obo)

@app.route('/admin_crud_actualizar_direccion/<int:id>')
@admin_required
def admin_crud_actualizar_direccion(id):
    usuario = controlador_usuario.obtener_direccion_id_mantenimiento(id)
    return render_template('CRUDS/DIRECCION/actualizar.html', usuario=usuario)

@app.route('/admin_crud_actualizar_direccion_completa' , methods=['POST'])
@admin_required
def admin_crud_actualizar_direccion_completa():
    id = request.form["id"]
    nombre= request.form["nombres"]
    email = request.form["email"]
    telefono = request.form["telefono"]
    apellido = request.form["apellidos"]
    nombre_usuario = request.form["usuario"]
    direccion = request.form["direccion"]
    id_usu = request.form["id_usu"]
    controlador_usuario.actualizar_direccion(nombre,email,telefono,apellido,nombre_usuario, direccion ,id_usu ,id)
    return redirect("/admin_crud_direccion_general")

@app.route('/admin_crud_insert_direccion', methods=['POST'])
@admin_required
def admin_crud_insert_direccion():
    email = request.form["nombres"]
    telefono = request.form["apellidos"]
    apellido = request.form["email"]
    nombre_usuario = request.form["telefono"]
    direccion_1 = request.form["direccion_1"]
    direccion_2 = request.form["direccion_2"]
    usuario = request.form["usuario"]
    if controlador_usuario.insertar_direccion(email,telefono,apellido,nombre_usuario, direccion_1, direccion_2 ,usuario):
        flash('direccion agregada correctamente')
        return redirect('/admin_crud_direccion_general')
    flash('Error al agregar la direccion')
    return redirect('/admin_crud_direccion_general')

@app.route('/admin_crud_eliminar_direccion', methods=['POST'])
@admin_required
def admin_crud_eliminar_direccion():
    controlador_usuario.eliminar_direccion(request.form["id"])
    return redirect("/admin_crud_direccion_general")

########categorias
@app.route('/admin_crud_categoria_general')
@admin_required
def admin_crud_categoria_general():
    usuarios = controlador_producto.obtener_nombre_categoria_api()
    return render_template('CRUDS/CATEGORIAS/general.html', usuarios=usuarios)

@app.route('/admin_crud_insertar_categoria')
@admin_required
def admin_crud_insertar_categoria():
    obo = controlador_usuario.obtener_usuarios()
    return render_template('CRUDS/CATEGORIAS/insert.html', obo=obo)

@app.route('/admin_crud_actualizar_categoria/<int:id>')
@admin_required
def admin_crud_actualizar_categoria(id):
    usuario = controlador_producto.obtener_nombre_categoria_por_id(id)
    return render_template('CRUDS/CATEGORIAS/actualizar.html', usuario=usuario)

@app.route('/admin_crud_actualizar_categoria_completa' , methods=['POST'])
@admin_required
def admin_crud_actualizar_categoria_completa():
    id = request.form["id"]
    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]
    fecha_creacion = request.form["fecha_creacion"]
    filas_actualizadas = controlador_producto.actualizar_categoria(nombre, descripcion, fecha_creacion, id)
    if filas_actualizadas:
        flash("Categoria actualizada correctamente", "success")
    else:
        flash("No se pudo actualizar la categoría", "error")
    return redirect("/admin_crud_categoria_general")

@app.route('/admin_crud_insert_categoria', methods=['POST'])
@admin_required
def admin_crud_insert_categoria():
    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]
    nuevo_id = controlador_producto.insertar_categoria(nombre, descripcion)
    if nuevo_id:
        flash("Categoría agregada correctamente", "success")
    else:
        flash("Error al agregar la categoría", "error")
    return redirect('/admin_crud_categoria_general')

@app.route('/admin_crud_eliminar_categoria', methods=['POST'])
@admin_required
def admin_crud_eliminar_categoria():
    controlador_producto.eliminar_categoria(request.form["id"])
    return redirect("/admin_crud_categoria_general")

########tipo usuario
@app.route('/admin_crud_tipo_user_general')
@admin_required
def admin_crud_tipo_user_general():
    usuarios = controlador_usuario.obtener_nombre_tipo_usuario()
    return render_template('CRUDS/TIPO USUARIO/general.html', usuarios=usuarios)

@app.route('/admin_crud_insertar_tipo_user')
@admin_required
def admin_crud_insertar_tipo_user():
    obo = controlador_usuario.obtener_usuarios()
    return render_template('CRUDS/TIPO USUARIO/insert.html', obo=obo)

@app.route('/admin_crud_actualizar_tipo_user/<int:id>')
@admin_required
def admin_crud_actualizar_tipo_user(id):
    usuario = controlador_usuario.obtener_nombre_tipo_usuario_x_id(id)
    return render_template('CRUDS/TIPO USUARIO/actualizar.html', usuario=usuario)

@app.route('/admin_crud_actualizar_tipo_user_completa' , methods=['POST'])
@admin_required
def admin_crud_actualizar_tipo_user_completa():
    id = request.form["id"]
    nombre= request.form["nombres"]
    controlador_usuario.actualizar_tipo_usuario(nombre, id)
    return redirect("/admin_crud_tipo_user_general")

@app.route('/admin_crud_insert_tipo_user', methods=['POST'])
@admin_required
def admin_crud_insert_tipo_user():
    email = request.form["nombres"]
    if controlador_usuario.insertar_tipo_usuario(email):
        flash('tipo usuario agregada correctamente')
        return redirect('/admin_crud_tipo_user_general')
    flash('Error al agregar tipo usuario')
    return redirect('/admin_crud_tipo_user_general')

@app.route('/admin_crud_eliminar_tipo_user', methods=['POST'])
@admin_required
def admin_crud_eliminar_tipo_user():
    controlador_usuario.eliminar_tipo_usuario(request.form["id"])
    return redirect("/admin_crud_tipo_user_general")

@app.route('/admin_crud_pedido_enviado_general')
@admin_required
def admin_crud_pedido_enviado_general():
    usuarios = controlador_usuario.ver_pedidos_general_enviados()
    return render_template('CRUDS/ENVIADOS/general.html', usuarios=usuarios)

@app.route('/admin_crud_pedido_PENDIENTE_general')
@admin_required
def admin_crud_pedido_PENDIENTE_general():
    usuarios = controlador_usuario.ver_pedidos_general_PENDIENTE()
    return render_template('CRUDS/PENDIENTES/general.html', usuarios=usuarios)

@app.route('/compras')
def compras():
    compras = controlador_usuario.obtener_compras()
    return render_template('compras.html', compras=compras)

@app.route('/compras/nueva', methods=['GET', 'POST'])
def crear_compra():
    if request.method == 'POST':
        controlador_usuario.guardar_compra(request.form)
        return redirect(url_for('compras'))
    else:
        proveedores = controlador_usuario.obtener_proveedores()
        insumos = controlador_producto.obtener_insumos()
        return render_template('crear_compra.html', proveedores=proveedores, insumos=insumos)

if __name__ == '__main__':
    app.run(debug=True)