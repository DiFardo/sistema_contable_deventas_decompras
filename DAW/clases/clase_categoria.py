class clsCategoria:
    id_categoria = 0
    nombre = ""
    descripcion = ""
    fecha_creacion = ""
    dic_categoria = dict()

    def __init__(self, p_id_categoria, p_nombre, p_descripcion, p_fecha_creacion):
        self.id_categoria = p_id_categoria
        self.nombre = p_nombre
        self.descripcion = p_descripcion
        self.fecha_creacion = p_fecha_creacion

        # Diccionario para almacenar los atributos de la categoría
        self.dic_categoria["id_categoria"] = p_id_categoria
        self.dic_categoria["nombre"] = p_nombre
        self.dic_categoria["descripcion"] = p_descripcion
        self.dic_categoria["fecha_creacion"] = p_fecha_creacion