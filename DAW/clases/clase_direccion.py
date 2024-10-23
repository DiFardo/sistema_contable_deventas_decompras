class clsDireccion:
    id = 0
    pais = ""
    departamento = ""
    ciudad = ""
    codigo_postal = ""
    direccion_1 = ""
    direccion_2 = ""
    id_usuario = 0
    dic_direccion = dict()

    def __init__(self, p_id, p_pais, p_departamento, p_ciudad, p_codigo_postal, p_direccion_1, p_direccion_2, p_id_usuario):
        self.id = p_id
        self.pais = p_pais
        self.departamento = p_departamento
        self.ciudad = p_ciudad
        self.codigo_postal = p_codigo_postal
        self.direccion_1 = p_direccion_1
        self.direccion_2 = p_direccion_2
        self.id_usuario = p_id_usuario

        self.dic_direccion["id"] = p_id
        self.dic_direccion["pais"] = p_pais
        self.dic_direccion["departamento"] = p_departamento
        self.dic_direccion["ciudad"] = p_ciudad
        self.dic_direccion["codigo_postal"] = p_codigo_postal
        self.dic_direccion["direccion_1"] = p_direccion_1
        self.dic_direccion["direccion_2"] = p_direccion_2
        self.dic_direccion["id_usuario"] = p_id_usuario