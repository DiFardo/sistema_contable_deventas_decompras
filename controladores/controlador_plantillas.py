from flask import send_file, jsonify
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.styles import Border, Side, Alignment, Font
from openpyxl.styles.numbers import FORMAT_DATE_DDMMYY, FORMAT_NUMBER_COMMA_SEPARATED1
from psycopg2.extras import DictCursor
from bd_conexion import obtener_conexion

def generar_registro_venta_excel(mes, anio):
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

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
            SUM(v.total) AS total_comprobante
        FROM ventas_contables v
        WHERE EXTRACT(MONTH FROM v.fecha) = %s AND EXTRACT(YEAR FROM v.fecha) = %s
        GROUP BY v.serie_comprobante, v.numero_comprobante, v.tipo_documento, 
                 v.numero_documento, v.usuario, v.tipo_comprobante, v.fecha
        ORDER BY v.fecha, v.serie_comprobante, v.numero_comprobante;
        """
        cursor.execute(consulta, (mes, anio))

        resultados = cursor.fetchall()

        ruta_plantilla = 'plantillas/RegistroVentas.xlsx'
        workbook = load_workbook(ruta_plantilla)
        hoja = workbook.active

        borde = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        fuente_estandar = Font(name='Arial', size=10)

        fila_base = 12
        alto_fila_base = hoja.row_dimensions[fila_base].height

        fila_inicial = fila_base
        total_base_imponible = 0
        total_igv = 0
        total_comprobante = 0

        columnas_con_borde = list(range(1, 23))

        for fila, registro in enumerate(resultados, start=fila_inicial):
            hoja.row_dimensions[fila].height = alto_fila_base

            celdas = [
                (1, registro[0]),  # Correlativo
                (2, registro[1]),  # Fecha de emisión
                (4, registro[2]),  # Tipo de comprobante
                (5, registro[3]),  # Serie comprobante
                (6, registro[4]),  # Número comprobante
                (7, registro[5]),  # Tipo documento
                (8, registro[6]),  # Número documento
                (9, registro[7]),  # Usuario
                (11, registro[8]),  # Base imponible
                (15, registro[9]),  # IGV
                (17, registro[10])  # Total comprobante
            ]

            for col in columnas_con_borde:
                celda = hoja.cell(row=fila, column=col)
                celda.border = borde
                celda.font = fuente_estandar

            for col, valor in celdas:
                celda = hoja.cell(row=fila, column=col, value=valor)
                celda.font = fuente_estandar

                if col in (11, 15, 17):
                    celda.alignment = Alignment(horizontal='right', vertical='center')
                    celda.number_format = FORMAT_NUMBER_COMMA_SEPARATED1
                elif col == 2:
                    celda.number_format = FORMAT_DATE_DDMMYY
                    celda.alignment = Alignment(horizontal='center', vertical='center')
                elif col == 6:
                    celda.alignment = Alignment(horizontal='center', vertical='center')
                else:
                    celda.alignment = Alignment(horizontal='left', vertical='center')

                if col == 11:
                    total_base_imponible += valor
                elif col == 15:
                    total_igv += valor
                elif col == 17:
                    total_comprobante += valor

        # Escribir los totales en la fila de "Totales"
        fila_totales = fila_inicial + len(resultados)
        hoja.row_dimensions[fila_totales].height = alto_fila_base
        celda_totales = hoja.cell(row=fila_totales, column=9, value="TOTALES")
        celda_totales.border = borde
        celda_totales.alignment = Alignment(horizontal='center', vertical='center')
        celda_totales.font = Font(name='Arial', size=10, bold=True)

        total_base_imponible_celda = hoja.cell(row=fila_totales, column=11, value=total_base_imponible)
        total_base_imponible_celda.border = borde
        total_base_imponible_celda.number_format = FORMAT_NUMBER_COMMA_SEPARATED1
        total_base_imponible_celda.alignment = Alignment(horizontal='right', vertical='center')
        total_base_imponible_celda.font = fuente_estandar

        total_igv_celda = hoja.cell(row=fila_totales, column=15, value=total_igv)
        total_igv_celda.border = borde
        total_igv_celda.number_format = FORMAT_NUMBER_COMMA_SEPARATED1
        total_igv_celda.alignment = Alignment(horizontal='right', vertical='center')
        total_igv_celda.font = fuente_estandar

        total_comprobante_celda = hoja.cell(row=fila_totales, column=17, value=total_comprobante)
        total_comprobante_celda.border = borde
        total_comprobante_celda.number_format = FORMAT_NUMBER_COMMA_SEPARATED1
        total_comprobante_celda.alignment = Alignment(horizontal='right', vertical='center')
        total_comprobante_celda.font = fuente_estandar

        for col in columnas_con_borde:
            hoja.cell(row=fila_totales, column=col).border = borde

        # Guardar el archivo Excel en memoria
        output = BytesIO()
        workbook.save(output)
        output.seek(0)

        nombre_archivo = f'registro_ventas_{anio}_{mes}.xlsx'

        # Enviar el archivo como respuesta
        return send_file(
            output,
            download_name=nombre_archivo,
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        print(f"Error al generar el registro de ventas: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conexion:
            cursor.close()
            conexion.close()

def obtener_registro_ventas(mes, año):
    conexion = obtener_conexion()
    registros = []
    total_base_imponible = 0
    total_igv = 0
    total_total_comprobante = 0

    with conexion.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("""
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
                SUM(v.total) AS total_comprobante
            FROM ventas_contables v
            WHERE EXTRACT(MONTH FROM v.fecha) = %s AND EXTRACT(YEAR FROM v.fecha) = %s
            GROUP BY v.serie_comprobante, v.numero_comprobante, v.tipo_documento, 
                     v.numero_documento, v.usuario, v.tipo_comprobante, v.fecha
            ORDER BY v. fecha, v.serie_comprobante, v.numero_comprobante;
        """, (mes, año))

        registros = cursor.fetchall()

        # Calcular los totales
        for registro in registros:
            total_base_imponible += registro['base_imponible']
            total_igv += registro['igv']
            total_total_comprobante += registro['total_comprobante']

    conexion.close()

    return registros, total_base_imponible, total_igv, total_total_comprobante

def obtener_registro_compras(mes, año):
    conexion = obtener_conexion()
    registros = []
    total_base_imponible = 0
    total_igv = 0
    total_total_comprobante = 0

    with conexion.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("""
            SELECT 
                ROW_NUMBER() OVER(ORDER BY c.serie_comprobante, c.numero_comprobante) AS correlativo,
                TO_CHAR(c.fecha, 'DD/MM/YYYY') AS fecha_emision,
                CASE WHEN c.tipo_comprobante = 'Factura' THEN '01' ELSE '03' END AS tipo_comprobante,
                c.serie_comprobante,
                c.numero_comprobante,
                CASE 
                    WHEN c.tipo_documento = 'DNI' THEN '1' 
                    WHEN c.tipo_documento = 'Carnet de extranjería' THEN '4'
                    WHEN c.tipo_documento = 'RUC' THEN '6'
                    WHEN c.tipo_documento = 'Pasaporte' THEN '7'
                    ELSE ''
                END AS tipo_documento,
                c.numero_documento,
                c.nombre_proveedor,
                SUM(c.sub_sin_igv) AS base_imponible,
                SUM(c.igv) AS igv,
                SUM(c.total) AS total_comprobante
            FROM compras_contables c
            WHERE EXTRACT(MONTH FROM c.fecha) = %s AND EXTRACT(YEAR FROM c.fecha) = %s
            GROUP BY c.serie_comprobante, c.numero_comprobante, c.tipo_documento, 
                     c.numero_documento, c.nombre_proveedor, c.tipo_comprobante, c.fecha
            ORDER BY c.fecha, c.serie_comprobante, c.numero_comprobante;
        """, (mes, año))

        registros = cursor.fetchall()

        # Calcular los totales
        for registro in registros:
            total_base_imponible += registro['base_imponible']
            total_igv += registro['igv']
            total_total_comprobante += registro['total_comprobante']

    conexion.close()

    return registros, total_base_imponible, total_igv, total_total_comprobante

def generar_registro_compra_excel(mes, anio):
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        consulta = """
            SELECT 
                ROW_NUMBER() OVER(ORDER BY c.serie_comprobante, c.numero_comprobante) AS correlativo,
                TO_CHAR(c.fecha, 'DD/MM/YYYY') AS fecha_emision,
                CASE WHEN c.tipo_comprobante = 'Factura' THEN '01' ELSE '03' END AS tipo_comprobante,
                c.serie_comprobante,
                c.numero_comprobante,
                CASE 
                    WHEN c.tipo_documento = 'DNI' THEN '1' 
                    WHEN c.tipo_documento = 'Carnet de extranjería' THEN '4'
                    WHEN c.tipo_documento = 'RUC' THEN '6'
                    WHEN c.tipo_documento = 'Pasaporte' THEN '7'
                    ELSE ''
                END AS tipo_documento,
                c.numero_documento,
                c.nombre_proveedor,
                SUM(c.sub_sin_igv) AS base_imponible,
                SUM(c.igv) AS igv,
                SUM(c.total) AS total_comprobante
            FROM compras_contables c
            WHERE EXTRACT(MONTH FROM c.fecha) = %s AND EXTRACT(YEAR FROM c.fecha) = %s
            GROUP BY c.serie_comprobante, c.numero_comprobante, c.tipo_documento, 
                     c.numero_documento, c.nombre_proveedor, c.tipo_comprobante, c.fecha
            ORDER BY c. fecha, c.serie_comprobante, c.numero_comprobante;
        """
        cursor.execute(consulta, (mes, anio))

        resultados = cursor.fetchall()

        ruta_plantilla = 'plantillas/RegistroCompras.xlsx'
        workbook = load_workbook(ruta_plantilla)
        hoja = workbook.active

        borde = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        fuente_estandar = Font(name='Arial', size=10)

        fila_base = 14
        alto_fila_base = hoja.row_dimensions[fila_base].height

        fila_inicial = fila_base
        total_base_imponible = 0
        total_igv = 0
        total_comprobante = 0

        columnas_con_borde = list(range(1, 29))

        for fila, registro in enumerate(resultados, start=fila_inicial):
            hoja.row_dimensions[fila].height = alto_fila_base

            celdas = [
                (1, registro[0]),  # Correlativo
                (2, registro[1]),  # Fecha de emisión
                (4, registro[2]),  # Tipo de comprobante
                (5, registro[3]),  # Serie comprobante
                (7, registro[4]),  # Número comprobante
                (8, registro[5]),  # Tipo documento
                (9, registro[6]),  # Número documento
                (10, registro[7]),  # Nombre proveedor
                (11, registro[8]),  # Base imponible
                (12, registro[9]),  # IGV
                (20, registro[10])  # Total comprobante
            ]

            for col in columnas_con_borde:
                celda = hoja.cell(row=fila, column=col)
                celda.border = borde
                celda.font = fuente_estandar

            for col, valor in celdas:
                celda = hoja.cell(row=fila, column=col, value=valor)
                celda.font = fuente_estandar

                if col in (11, 12, 20):
                    celda.alignment = Alignment(horizontal='right', vertical='center')
                    celda.number_format = FORMAT_NUMBER_COMMA_SEPARATED1
                elif col == 2:
                    celda.number_format = FORMAT_DATE_DDMMYY
                    celda.alignment = Alignment(horizontal='center', vertical='center')
                elif col == 7:
                    celda.alignment = Alignment(horizontal='center', vertical='center')
                else:
                    celda.alignment = Alignment(horizontal='left', vertical='center')

                if col == 11:
                    total_base_imponible += valor
                elif col == 12:
                    total_igv += valor
                elif col == 20:
                    total_comprobante += valor

        # Escribir los totales en la fila de "Totales"
        fila_totales = fila_inicial + len(resultados)
        hoja.row_dimensions[fila_totales].height = alto_fila_base
        celda_totales = hoja.cell(row=fila_totales, column=10, value="TOTALES")
        celda_totales.border = borde
        celda_totales.alignment = Alignment(horizontal='center', vertical='center')
        celda_totales.font = Font(name='Arial', size=10, bold=True)

        total_base_imponible_celda = hoja.cell(row=fila_totales, column=11, value=total_base_imponible)
        total_base_imponible_celda.border = borde
        total_base_imponible_celda.number_format = FORMAT_NUMBER_COMMA_SEPARATED1
        total_base_imponible_celda.alignment = Alignment(horizontal='right', vertical='center')
        total_base_imponible_celda.font = fuente_estandar

        total_igv_celda = hoja.cell(row=fila_totales, column=12, value=total_igv)
        total_igv_celda.border = borde
        total_igv_celda.number_format = FORMAT_NUMBER_COMMA_SEPARATED1
        total_igv_celda.alignment = Alignment(horizontal='right', vertical='center')
        total_igv_celda.font = fuente_estandar

        total_comprobante_celda = hoja.cell(row=fila_totales, column=20, value=total_comprobante)
        total_comprobante_celda.border = borde
        total_comprobante_celda.number_format = FORMAT_NUMBER_COMMA_SEPARATED1
        total_comprobante_celda.alignment = Alignment(horizontal='right', vertical='center')
        total_comprobante_celda.font = fuente_estandar

        for col in columnas_con_borde:
            hoja.cell(row=fila_totales, column=col).border = borde

        # Guardar el archivo Excel en memoria
        output = BytesIO()
        workbook.save(output)
        output.seek(0)

        nombre_archivo = f'registro_compras_{anio}_{mes}.xlsx'

        # Enviar el archivo como respuesta
        return send_file(
            output,
            download_name=nombre_archivo,
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        print(f"Error al generar el registro de compras: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conexion:
            cursor.close()
            conexion.close()