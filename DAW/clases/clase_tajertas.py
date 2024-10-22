class clsTarjeta: 
    id_tarjeta = 0
    numero_tarjeta = ""
    nombre_titular = ""
    fecha_vencimiento = ""
    cvv = ""
    id_usuario = 0
    dic_tarjeta = dict()
    
    def __init__(self, id_tarjeta, numero_tarjeta, nombre_titular, fecha_vencimiento, cvv, id_usuario):
        self.id_tarjeta = id_tarjeta
        self.numero_tarjeta = numero_tarjeta
        self.nombre_titular = nombre_titular
        self.fecha_vencimiento = fecha_vencimiento
        self.cvv = cvv
        self.id_usuario = id_usuario
        
        # Diccionario con los datos de la tarjeta estandarizados
        self.dic_tarjeta["id_tarjeta"] = id_tarjeta
        self.dic_tarjeta["numero_tarjeta"] = numero_tarjeta
        self.dic_tarjeta["nombre_titular"] = nombre_titular
        self.dic_tarjeta["fecha_vencimiento"] = fecha_vencimiento
        self.dic_tarjeta["cvv"] = cvv
        self.dic_tarjeta["id_usuario"] = id_usuario