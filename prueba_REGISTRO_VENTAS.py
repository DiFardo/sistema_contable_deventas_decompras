import psycopg2
from openpyxl import load_workbook
from bd_conexion import obtener_conexion

def generar_registro_venta_excel(mes, anio, ruta_plantilla, ruta_salida):
    try:
        # Establecer conexión con la base de datos
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Ejecutar la consulta SQL
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
                WHEN v.tipo_documento = 'RUC' THEN '6'
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

        # Obtener los resultados de la consulta
        resultados = cursor.fetchall()

        # Cargar la plantilla de Excel
        workbook = load_workbook(ruta_plantilla)
        hoja = workbook.active

        # Insertar los datos en la plantilla
        fila_inicial = 12  # Supongamos que los datos comienzan en la fila 2
        for fila, registro in enumerate(resultados, start=fila_inicial):
            hoja.cell(row=fila, column=1, value=registro[0])  # correlativo
            hoja.cell(row=fila, column=2, value=registro[1])  # fecha_emision
            hoja.cell(row=fila, column=4, value=registro[2])  # tipo_comprobante
            hoja.cell(row=fila, column=5, value=registro[3])  # serie_comprobante
            hoja.cell(row=fila, column=6, value=registro[4])  # numero_comprobante
            hoja.cell(row=fila, column=7, value=registro[5])  # tipo_documento
            hoja.cell(row=fila, column=8, value=registro[6])  # numero_documento
            hoja.cell(row=fila, column=9, value=registro[7])  # usuario
            hoja.cell(row=fila, column=10, value=registro[8])  # base_imponible
            hoja.cell(row=fila, column=14, value=registro[9])  # igv
            hoja.cell(row=fila, column=16, value=registro[10])  # total_comprobante

        # Guardar el nuevo archivo de Excel
        workbook.save(ruta_salida)
        print(f"Registro de ventas generado exitosamente en: {ruta_salida}")

    except Exception as e:
        print(f"Error al generar el registro de ventas: {e}")
    finally:
        # Cerrar la conexión con la base de datos
        if conexion:
            cursor.close()
            conexion.close()

# Ejemplo de uso
mes = 10  # Octubre
anio = 2024  # Año 2024
ruta_plantilla = 'plantillas/RegistroVentas.xlsx'
ruta_salida = f'registro_ventas_{anio}_{mes}.xlsx'

generar_registro_venta_excel(mes, anio, ruta_plantilla, ruta_salida)