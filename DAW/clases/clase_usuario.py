class clsUsuario:
    id_usuario = 0
    nombre = ""
    email = ""
    telefono = ""
    apellido = ""
    nombre_usuario = ""
    contrasena = ""
    fecha_nacimiento = ""
    fecha_creacion = ""
    tipo_usuario_id = 0
    diccionario_usuario = dict()

    def __init__(self, p_id_usuario, p_nombre, p_email, p_telefono, p_apellido, p_nombre_usuario, p_contrasena, p_fecha_nacimiento, p_fecha_creacion, p_tipo_usuario_id):
        self.id_usuario = p_id_usuario
        self.nombre = p_nombre
        self.email = p_email
        self.telefono = p_telefono
        self.apellido = p_apellido
        self.nombre_usuario = p_nombre_usuario
        self.contrasena = p_contrasena
        self.fecha_nacimiento = p_fecha_nacimiento
        self.fecha_creacion = p_fecha_creacion
        self.tipo_usuario_id = p_tipo_usuario_id

        self.diccionario_usuario["id_usuario"] = p_id_usuario
        self.diccionario_usuario["nombre"] = p_nombre
        self.diccionario_usuario["email"] = p_email
        self.diccionario_usuario["telefono"] = p_telefono
        self.diccionario_usuario["apellido"] = p_apellido
        self.diccionario_usuario["nombre_usuario"] = p_nombre_usuario
        self.diccionario_usuario["contrasena"] = p_contrasena
        self.diccionario_usuario["fecha_nacimiento"] = p_fecha_nacimiento
        self.diccionario_usuario["fecha_creacion"] = p_fecha_creacion
        self.diccionario_usuario["tipo_usuario_id"] = p_tipo_usuario_id