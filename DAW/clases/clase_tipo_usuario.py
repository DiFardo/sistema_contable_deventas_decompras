class clsTipoUsuario:
    id_tipo_usuario = 0
    nombre_tipo_usuario = ""
    diccionario_tipo_usuario = dict()

    def __init__(self, id_tipo, nombre_tipo):
        self.id_tipo_usuario = id_tipo
        self.nombre_tipo_usuario = nombre_tipo
        
        self.diccionario_tipo_usuario["id_tipo_usuario"] = id_tipo
        self.diccionario_tipo_usuario["nombre_tipo_usuario"] = nombre_tipo