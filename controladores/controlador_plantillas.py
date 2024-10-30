from flask import send_file, jsonify
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.styles import Border, Side, Alignment, Font
from openpyxl.styles.numbers import FORMAT_DATE_DDMMYY, FORMAT_NUMBER_COMMA_SEPARATED1
from bd_conexion import obtener_conexion

def generar_registro_venta_excel(mes, anio):
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
        ruta_plantilla = 'plantillas/RegistroVentas.xlsx'
        workbook = load_workbook(ruta_plantilla)
        hoja = workbook.active

        # Estilo de bordes para las celdas
        borde = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # Definir la fuente estándar Arial 10
        fuente_estandar = Font(name='Arial', size=10)

        # Copiar el estilo de la fila base (por ejemplo, la fila 12)
        fila_base = 12
        alto_fila_base = hoja.row_dimensions[fila_base].height

        # Insertar los datos en la plantilla
        fila_inicial = fila_base
        total_base_imponible = 0
        total_igv = 0
        total_comprobante = 0

        # Columnas a las que se les aplicará borde, incluso si están vacías
        columnas_con_borde = list(range(1, 23))

        for fila, registro in enumerate(resultados, start=fila_inicial):
            hoja.row_dimensions[fila].height = alto_fila_base

            # Insertar valores y aplicar estilos a las celdas
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

                # Justificar a la derecha si la columna es de números
                if col in (11, 15, 17):
                    celda.alignment = Alignment(horizontal='right', vertical='center')
                    celda.number_format = FORMAT_NUMBER_COMMA_SEPARATED1
                elif col == 2:
                    celda.number_format = FORMAT_DATE_DDMMYY
                    celda.alignment = Alignment(horizontal='center', vertical='center')
                else:
                    celda.alignment = Alignment(horizontal='left', vertical='center')

                # Sumar totales
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