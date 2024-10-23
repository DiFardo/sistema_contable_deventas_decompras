class clsPago:
    id_pago = 0
    id_pedido = 0
    id_tarjeta = 0
    fecha_pago = ""
    monto = 0.0
    estado_pago = ""
    dic_pago = dict()
    
    def __init__(self, id_pago, id_pedido, id_tarjeta, fecha_pago, monto, estado_pago):
        self.id_pago = id_pago
        self.id_pedido = id_pedido
        self.id_tarjeta = id_tarjeta
        self.fecha_pago = fecha_pago
        self.monto = monto
        self.estado_pago = estado_pago
        
        self.dic_pago["id_pago"] = id_pago
        self.dic_pago["id_pedido"] = id_pedido
        self.dic_pago["id_tarjeta"] = id_tarjeta
        self.dic_pago["fecha_pago"] = fecha_pago
        self.dic_pago["monto"] = monto
        self.dic_pago["estado_pago"] = estado_pago
