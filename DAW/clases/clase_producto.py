class clsProducto:
    id_producto = 0
    nombre_producto = ""
    descripcion = ""
    precio = 0.0
    stock = 0
    id_categoria = 0
    imagen = ""
    fecha_creacion = ""
    talla = ""
    genero = ""
    dicc_producto = dict()

    def __init__(self, p_id_producto, p_nombre_producto, p_descripcion, p_precio, p_stock, p_id_categoria, p_imagen, p_fecha_creacion, p_talla, p_genero):
        self.id_producto = p_id_producto
        self.nombre_producto = p_nombre_producto
        self.descripcion = p_descripcion
        self.precio = p_precio
        self.stock = p_stock
        self.id_categoria = p_id_categoria
        self.imagen = p_imagen
        self.fecha_creacion = p_fecha_creacion
        self.talla = p_talla
        self.genero = p_genero

        # Diccionario actualizado con nombres estandarizados
        self.dicc_producto["id_producto"] = p_id_producto
        self.dicc_producto["nombre_producto"] = p_nombre_producto
        self.dicc_producto["descripcion"] = p_descripcion
        self.dicc_producto["precio"] = p_precio
        self.dicc_producto["stock"] = p_stock
        self.dicc_producto["id_categoria"] = p_id_categoria
        self.dicc_producto["imagen"] = p_imagen
        self.dicc_producto["fecha_creacion"] = p_fecha_creacion
        self.dicc_producto["talla"] = p_talla
        self.dicc_producto["genero"] = p_genero