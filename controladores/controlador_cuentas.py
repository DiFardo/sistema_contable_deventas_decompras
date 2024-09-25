from bd_conexion import obtener_conexion

def obtener_todas_cuentas():
    conexion = obtener_conexion()
    cuentas = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT  codigo, descripcion FROM cuentas ORDER BY 1")
        cuentas = cursor.fetchall()
    conexion.close()
    return cuentas