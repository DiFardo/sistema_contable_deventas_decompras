from bd_conexion import obtener_conexion
import openpyxl
from datetime import datetime

def generar_registro_ventas(mes, anio, ruta_excel):
    # Conectar a la base de datos
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Consultar las ventas agrupadas por comprobante y dentro del mes y año especificados
    consulta = """
        SELECT 
            ROW_NUMBER() OVER(ORDER BY v.serie_comprobante, v.numero_comprobante) AS correlativo,
            TO_CHAR(v.fecha, 'DD/MM/YYYY') AS fecha_emision,
            CASE WHEN v.tipo_comprobante = 'Boleta' THEN '03' ELSE '01' END AS tipo_comprobante,
            v.serie_comprobante,
            v.numero_comprobante,
            CASE 
                WHEN v.tipo_documento = 'DNI' THEN '1' 
                WHEN v.tipo_documento = 'Carnet de extranjería' THEN '4'
                WHEN v.tipo_documento = 'Pasaporte' THEN '7'
                ELSE ''
            END AS tipo_documento,
            v.numero_documento,
            v.usuario,
            SUM(v.sub_sin_igv) AS base_imponible,
            SUM(v.igv) AS igv,
            SUM(v.subtotal) AS total_comprobante
        FROM ventas_contables v
        WHERE EXTRACT(MONTH FROM v.fecha) = %s AND EXTRACT(YEAR FROM v.fecha) = %s
        GROUP BY v.serie_comprobante, v.numero_comprobante, v.tipo_documento, 
                 v.numero_documento, v.usuario, v.tipo_comprobante, v.fecha
        ORDER BY v.serie_comprobante, v.numero_comprobante;
    """

    cursor.execute(consulta, (mes, anio))
    ventas = cursor.fetchall()

    # Cargar la plantilla de Excel
    wb = openpyxl.load_workbook(ruta_excel)
    ws = wb.active

    # Definir la fila inicial donde se empezará a rellenar el Excel
    fila_inicial = 10

    # Rellenar el Excel con los datos obtenidos de la consulta
    for idx, venta in enumerate(ventas, start=fila_inicial):
        ws.cell(row=idx, column=1).value = venta[0]  # Correlativo
        ws.cell(row=idx, column=2).value = venta[1]  # Fecha de emisión
        ws.cell(row=idx, column=3).value = venta[2]  # Tipo de comprobante
        ws.cell(row=idx, column=4).value = venta[3]  # Serie
        ws.cell(row=idx, column=5).value = venta[4]  # Número de comprobante
        ws.cell(row=idx, column=6).value = venta[5]  # Tipo de documento
        ws.cell(row=idx, column=7).value = venta[6]  # Número de documento
        ws.cell(row=idx, column=8).value = venta[7]  # Apellidos y nombres / Razón social
        ws.cell(row=idx, column=9).value = venta[8]  # Base imponible
        ws.cell(row=idx, column=10).value = venta[9]  # IGV
        ws.cell(row=idx, column=11).value = venta[10]  # Importe total

    # Guardar el archivo Excel con los datos completados
    wb.save(ruta_excel)

    # Cerrar la conexión y el cursor
    cursor.close()
    conexion.close()

    print(f"Registro de ventas para {mes}/{anio} generado exitosamente en {ruta_excel}.")

# Ejemplo de uso:
generar_registro_ventas(10, 2024, '/mnt/data/234_formato141.xls')