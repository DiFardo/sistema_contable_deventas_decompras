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
        
        periodo = f"{anio}-{str(mes).zfill(2)}"
        hoja.cell(row=3, column=2, value=periodo)

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

        periodo = f"{anio}-{str(mes).zfill(2)}"
        hoja.cell(row=3, column=2, value=periodo)

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

def generar_libro_diario_excel(fecha):
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        consulta = """
            SELECT
                DENSE_RANK() OVER (ORDER BY ac.numero_asiento) AS numero_correlativo,
                TO_CHAR(ac.fecha, 'DD/MM/YYYY') AS fecha,
                CASE
                    WHEN m.tipo_movimiento = 'Ventas' THEN 'Por la venta de mercadería'
                    WHEN m.tipo_movimiento = 'Compras' THEN 'Por la compra de insumos'
                    ELSE ''
                END AS glosa,
                CASE
                    WHEN m.tipo_movimiento = 'Compras' THEN 8
                    WHEN m.tipo_movimiento = 'Ventas' THEN 14
                    ELSE NULL
                END AS codigo_del_libro,
                DENSE_RANK() OVER (ORDER BY ac.numero_asiento) AS numero_correlativo_documento,
                ac.numero_documento AS numero_documento_sustentatorio,
                ac.codigo_cuenta,
                ac.denominacion,
                ac.debe,
                ac.haber
            FROM asientos_contables ac
            JOIN movimientos m ON ac.numero_asiento = m.movimiento_id
            WHERE ac.fecha::date = %s::date
            ORDER BY numero_correlativo, ac.id;
        """
        cursor.execute(consulta, (fecha,))
        resultados = cursor.fetchall()

        ruta_plantilla = 'plantillas/LibroDiario.xlsx'
        workbook = load_workbook(ruta_plantilla)
        hoja = workbook.active

        borde = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        fuente_estandar = Font(name='Arial', size=10)

        hoja.cell(row=3, column=2, value=fecha)

        fila_base = 11
        alto_fila_base = hoja.row_dimensions[fila_base].height

        fila_inicial = fila_base
        total_debe = 0
        total_haber = 0

        columnas_con_borde = list(range(1, 11))

        for fila, registro in enumerate(resultados, start=fila_inicial):
            hoja.row_dimensions[fila].height = alto_fila_base

            celdas = [
                (1, registro[0]),  # Correlativo
                (2, registro[1]),  # Fecha
                (3, registro[2]),  # Glosa
                (4, registro[3]),  # Código del libro
                (5, registro[4]),  # Número correlativo del documento
                (6, registro[5]),  # Número documento sustentatorio
                (7, registro[6]),  # Código cuenta
                (8, registro[7]),  # Denominación
                (9, registro[8]),  # Debe
                (10, registro[9])  # Haber
            ]

            for col in columnas_con_borde:
                celda = hoja.cell(row=fila, column=col)
                celda.border = borde
                celda.font = fuente_estandar

            for col, valor in celdas:
                celda = hoja.cell(row=fila, column=col, value=valor)
                celda.font = fuente_estandar

                if col in (9, 10):
                    celda.alignment = Alignment(horizontal='right', vertical='center')
                    celda.number_format = FORMAT_NUMBER_COMMA_SEPARATED1
                elif col == 2:
                    celda.number_format = FORMAT_DATE_DDMMYY
                    celda.alignment = Alignment(horizontal='center', vertical='center')
                elif col == 6:
                    celda.alignment = Alignment(horizontal='center', vertical='center')
                else:
                    celda.alignment = Alignment(horizontal='left', vertical='center')

                if col == 9:
                    total_debe += valor or 0
                elif col == 10:
                    total_haber += valor or 0

        fila_totales = fila_inicial + len(resultados)
        hoja.row_dimensions[fila_totales].height = alto_fila_base
        celda_totales = hoja.cell(row=fila_totales, column=8, value="TOTALES")
        celda_totales.border = borde
        celda_totales.alignment = Alignment(horizontal='center', vertical='center')
        celda_totales.font = Font(name='Arial', size=10, bold=True)

        total_debe_celda = hoja.cell(row=fila_totales, column=9, value=total_debe)
        total_debe_celda.border = borde
        total_debe_celda.number_format = FORMAT_NUMBER_COMMA_SEPARATED1
        total_debe_celda.alignment = Alignment(horizontal='right', vertical='center')
        total_debe_celda.font = fuente_estandar

        total_haber_celda = hoja.cell(row=fila_totales, column=10, value=total_haber)
        total_haber_celda.border = borde
        total_haber_celda.number_format = FORMAT_NUMBER_COMMA_SEPARATED1
        total_haber_celda.alignment = Alignment(horizontal='right', vertical='center')
        total_haber_celda.font = fuente_estandar

        for col in columnas_con_borde:
            hoja.cell(row=fila_totales, column=col).border = borde

        output = BytesIO()
        workbook.save(output)
        output.seek(0)

        nombre_archivo = f'libro_diario_{fecha}.xlsx'

        return send_file(
            output,
            download_name=nombre_archivo,
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        print(f"Error al generar el libro diario: {e}")
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

        for registro in registros:
            total_base_imponible += registro['base_imponible']
            total_igv += registro['igv']
            total_total_comprobante += registro['total_comprobante']

    conexion.close()

    return registros, total_base_imponible, total_igv, total_total_comprobante

# Esta función realiza la consulta a la base de datos con el filtro de mes y año
def obtener_registro_ventas_por_fecha(mes, anio):
    conexion = obtener_conexion()
    registros = []
    total_base_imponible = 0
    total_igv = 0
    total_total_comprobante = 0

    with conexion.cursor(cursor_factory=DictCursor) as cursor:
        try:
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
                ORDER BY v.fecha, v.serie_comprobante, v.numero_comprobante;
            """, (mes, anio))

            registros = cursor.fetchall()

            for registro in registros:
                total_base_imponible += registro['base_imponible']
                total_igv += registro['igv']
                total_total_comprobante += registro['total_comprobante']
            
            # Log output for debugging
            print(f"Registros obtenidos: {registros}")
            print(f"Total Base Imponible: {total_base_imponible}, Total IGV: {total_igv}, Total Comprobante: {total_total_comprobante}")
        
        except Exception as e:
            print(f"Error al obtener registros de ventas: {e}")

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

        for registro in registros:
            total_base_imponible += registro['base_imponible']
            total_igv += registro['igv']
            total_total_comprobante += registro['total_comprobante']

    conexion.close()

    return registros, total_base_imponible, total_igv, total_total_comprobante


def obtener_registro_compras_por_fecha(mes, anio):
    conexion = obtener_conexion()
    registros = []
    total_base_imponible = 0
    total_igv = 0
    total_total_comprobante = 0

    with conexion.cursor(cursor_factory=DictCursor) as cursor:
        try:
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
            """, (mes, anio))

            registros = cursor.fetchall()

            for registro in registros:
                total_base_imponible += registro['base_imponible']
                total_igv += registro['igv']
                total_total_comprobante += registro['total_comprobante']

            # Log output for debugging
            print(f"Registros obtenidos: {registros}")
            print(f"Total Base Imponible: {total_base_imponible}, Total IGV: {total_igv}, Total Comprobante: {total_total_comprobante}")

        except Exception as e:
            print(f"Error al obtener registros de compras: {e}")

    conexion.close()

    return registros, total_base_imponible, total_igv, total_total_comprobante


def obtener_libro_diario(fecha):
    conexion = obtener_conexion()
    movimientos = []
    total_debe = 0
    total_haber = 0

    with conexion.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("""
            SELECT
                DENSE_RANK() OVER (ORDER BY ac.numero_asiento) AS numero_correlativo,
                ac.fecha,
                CASE
                    WHEN m.tipo_movimiento = 'Ventas' THEN 'Por la venta de mercadería'
                    WHEN m.tipo_movimiento = 'Compras' THEN 'Por la compra de insumos'
                    ELSE ''
                END AS glosa,
                CASE
                    WHEN m.tipo_movimiento = 'Compras' THEN 8
                    WHEN m.tipo_movimiento = 'Ventas' THEN 14
                    ELSE NULL
                END AS codigo_del_libro,
                DENSE_RANK() OVER (ORDER BY ac.numero_asiento) AS numero_correlativo_documento,
                ac.numero_documento AS numero_documento_sustentatorio,
                ac.codigo_cuenta,
                ac.denominacion,
                ac.debe,
                ac.haber
            FROM asientos_contables ac
            JOIN movimientos m ON ac.numero_asiento = m.movimiento_id
            WHERE ac.fecha::date = %s::date
            ORDER BY numero_correlativo, ac.id;
        """, (fecha,))
        
        movimientos = cursor.fetchall()

        for movimiento in movimientos:
            total_debe += movimiento['debe'] or 0
            total_haber += movimiento['haber'] or 0

    conexion.close()
    return movimientos, total_debe, total_haber


def obtener_libro_diario_por_fecha(fecha):
    conexion = obtener_conexion()
    movimientos = []
    total_debe = 0
    total_haber = 0

    with conexion.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("""
            SELECT
                DENSE_RANK() OVER (ORDER BY ac.numero_asiento) AS numero_correlativo,
                TO_CHAR(ac.fecha, 'DD/MM/YYYY') AS fecha,
                CASE
                    WHEN m.tipo_movimiento = 'Ventas' THEN 'Por la venta de mercadería'
                    WHEN m.tipo_movimiento = 'Compras' THEN 'Por la compra de insumos'
                    ELSE ''
                END AS glosa,
                CASE
                    WHEN m.tipo_movimiento = 'Compras' THEN 8
                    WHEN m.tipo_movimiento = 'Ventas' THEN 14
                    ELSE NULL
                END AS codigo_del_libro,
                DENSE_RANK() OVER (ORDER BY ac.numero_asiento) AS numero_correlativo_documento,
                ac.numero_documento AS numero_documento_sustentatorio,
                ac.codigo_cuenta,
                ac.denominacion,
                ac.debe,
                ac.haber
            FROM asientos_contables ac
            JOIN movimientos m ON ac.numero_asiento = m.movimiento_id
            WHERE ac.fecha::date = %s::date
            ORDER BY numero_correlativo, ac.id;
        """, (fecha,))

        movimientos = cursor.fetchall()

        for movimiento in movimientos:
            total_debe += movimiento['debe'] or 0
            total_haber += movimiento['haber'] or 0

    conexion.close()
    return movimientos, total_debe, total_haber

def obtener_libro_caja():
    conexion = obtener_conexion()
    movimientos_caja = []
    total_deudor = 0
    total_acreedor = 0

    with conexion.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("""
            SELECT
                DENSE_RANK() OVER (ORDER BY ac.numero_asiento) AS numero_correlativo,
                ac.fecha AS fecha_operacion,
                CASE
                    WHEN m.tipo_movimiento = 'Compras' THEN 'Por la compra de insumos'
                    WHEN m.tipo_movimiento = 'Ventas' THEN 'Por la venta de mercadería'
                    ELSE 'Descripción no especificada'
                END AS descripcion_operacion,
                ac.codigo_cuenta AS codigo_cuenta_asociada,
                ac.denominacion AS denominacion_cuenta_asociada,
                COALESCE(ac.debe, 0) AS saldo_deudor,  -- Usa COALESCE para reemplazar NULL por 0
                COALESCE(ac.haber, 0) AS saldo_acreedor  -- Usa COALESCE para reemplazar NULL por 0
            FROM asientos_contables ac
            JOIN movimientos m ON ac.numero_asiento = m.movimiento_id
            WHERE 
                ac.codigo_cuenta LIKE '12%'  
                OR ac.codigo_cuenta LIKE '42%'
            ORDER BY numero_correlativo, ac.id;
        """)

        movimientos_caja = cursor.fetchall()

        # Sumar totales considerando que ya no habrá None
        for movimiento in movimientos_caja:
            total_deudor += movimiento["saldo_deudor"]
            total_acreedor += movimiento["saldo_acreedor"]

    conexion.close()
    return movimientos_caja, total_deudor, total_acreedor




def obtener_cuentas_distintas():
    conexion = obtener_conexion()
    cuentas = []

    with conexion.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("""
            SELECT DISTINCT ac.codigo_cuenta
            FROM asientos_contables ac
            JOIN movimientos m ON ac.numero_asiento = m.movimiento_id
            WHERE EXTRACT(MONTH FROM ac.fecha) = 11
              AND EXTRACT(YEAR FROM ac.fecha) = 2024
              AND (ac.debe IS NOT NULL AND ac.debe != 0 OR ac.haber IS NOT NULL AND ac.haber != 0)
            ORDER BY ac.codigo_cuenta;
        """)
        
        cuentas = cursor.fetchall()

    conexion.close()
    return cuentas

def obtener_libro_mayor(mes, año, cuenta):
    conexion = obtener_conexion()
    movimientos = []

    with conexion.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("""
            SELECT fecha, numero_correlativo, glosa, debe as deudor, haber as acreedor
            FROM (
                SELECT
                    DENSE_RANK() OVER (ORDER BY ac.numero_asiento) AS numero_correlativo,
                    ac.fecha,
                    CASE
                        WHEN m.tipo_movimiento = 'Ventas' THEN 'Por la venta de mercadería'
                        WHEN m.tipo_movimiento = 'Compras' THEN 'Por la compra de insumos'
                        ELSE ''
                    END AS glosa,
                    ac.debe,
                    ac.haber
                FROM asientos_contables ac
                JOIN movimientos m ON ac.numero_asiento = m.movimiento_id
                WHERE EXTRACT(MONTH FROM ac.fecha) = %s
                AND EXTRACT(YEAR FROM ac.fecha) = %s
                AND ac.codigo_cuenta = %s
                AND (ac.debe IS NOT NULL AND ac.debe != 0 OR ac.haber IS NOT NULL AND ac.haber != 0)
                ORDER BY numero_correlativo, ac.id
            ) AS subquery;
        """, (mes, año, cuenta))
        
        movimientos = cursor.fetchall()
        print("Movimientos encontrados:", movimientos)  # Mensaje de depuración para ver el resultado de la consulta.

    conexion.close()
    return movimientos


def generar_libro_mayor_excel(mes, año, cuenta):
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        consulta = """
            SELECT fecha, numero_correlativo, glosa, debe as deudor, haber as acreedor
            FROM (
                SELECT
                    DENSE_RANK() OVER (ORDER BY ac.numero_asiento) AS numero_correlativo,
                    ac.fecha,
                    CASE
                        WHEN m.tipo_movimiento = 'Ventas' THEN 'Por la venta de mercadería'
                        WHEN m.tipo_movimiento = 'Compras' THEN 'Por la compra de insumos'
                        ELSE ''
                    END AS glosa,
                    ac.debe,
                    ac.haber
                FROM asientos_contables ac
                JOIN movimientos m ON ac.numero_asiento = m.movimiento_id
                WHERE EXTRACT(MONTH FROM ac.fecha) = %s
                AND EXTRACT(YEAR FROM ac.fecha) = %s
                AND ac.codigo_cuenta = %s
                AND (ac.debe IS NOT NULL AND ac.debe != 0 OR ac.haber IS NOT NULL AND ac.haber != 0)
                ORDER BY numero_correlativo, ac.id
            ) AS subquery;
        """
        cursor.execute(consulta, (mes, año, cuenta))
        resultados = cursor.fetchall()

        # Cargar plantilla y configurar hoja de trabajo
        ruta_plantilla = 'plantillas/LibroMayor.xlsx'
        workbook = load_workbook(ruta_plantilla)
        hoja = workbook.active

        # Agregar el período en la celda B3
        periodo = f"{año}-{mes.zfill(2)}"  # Formato de período YYYY-MM
        hoja.cell(row=3, column=2, value=periodo)

        # Agregar el código de la cuenta en la celda C6
        hoja.cell(row=6, column=3, value=cuenta)

        borde = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        fuente_estandar = Font(name='Arial', size=10)

        fila_base = 11
        alto_fila_base = hoja.row_dimensions[fila_base].height
        fila_inicial = fila_base
        total_deudor = 0
        total_acreedor = 0

        # Columnas con bordes aplicados
        columnas_con_borde = list(range(1, 6))

        # Llenar filas con los datos obtenidos
        for fila, registro in enumerate(resultados, start=fila_inicial):
            hoja.row_dimensions[fila].height = alto_fila_base
            celdas = [
                (1, registro[0]),  # Fecha
                (2, registro[1]),  # Número Correlativo
                (3, registro[2]),  # Glosa
                (4, registro[3]),  # Deudor
                (5, registro[4])   # Acreedor
            ]

            # Aplicar estilos y bordes
            for col in columnas_con_borde:
                celda = hoja.cell(row=fila, column=col)
                celda.border = borde
                celda.font = fuente_estandar

            for col, valor in celdas:
                celda = hoja.cell(row=fila, column=col, value=valor)
                celda.font = fuente_estandar

                if col in (4, 5):  # Columnas Deudor y Acreedor
                    celda.alignment = Alignment(horizontal='right', vertical='center')
                    celda.number_format = FORMAT_NUMBER_COMMA_SEPARATED1
                elif col == 1:  # Fecha
                    celda.number_format = FORMAT_DATE_DDMMYY
                    celda.alignment = Alignment(horizontal='center', vertical='center')
                else:
                    celda.alignment = Alignment(horizontal='left', vertical='center')

                if col == 4:
                    total_deudor += valor or 0
                elif col == 5:
                    total_acreedor += valor or 0

        # Agregar fila de totales
        fila_totales = fila_inicial + len(resultados)
        hoja.row_dimensions[fila_totales].height = alto_fila_base
        hoja.cell(row=fila_totales, column=3, value="TOTALES").border = borde
        hoja.cell(row=fila_totales, column=3).alignment = Alignment(horizontal='center', vertical='center')
        hoja.cell(row=fila_totales, column=3).font = Font(name='Arial', size=10, bold=True)

        hoja.cell(row=fila_totales, column=4, value=total_deudor).border = borde
        hoja.cell(row=fila_totales, column=4).number_format = FORMAT_NUMBER_COMMA_SEPARATED1
        hoja.cell(row=fila_totales, column=4).alignment = Alignment(horizontal='right', vertical='center')
        hoja.cell(row=fila_totales, column=4).font = fuente_estandar

        hoja.cell(row=fila_totales, column=5, value=total_acreedor).border = borde
        hoja.cell(row=fila_totales, column=5).number_format = FORMAT_NUMBER_COMMA_SEPARATED1
        hoja.cell(row=fila_totales, column=5).alignment = Alignment(horizontal='right', vertical='center')
        hoja.cell(row=fila_totales, column=5).font = fuente_estandar

        # Guardar el archivo en memoria para su descarga
        output = BytesIO()
        workbook.save(output)
        output.seek(0)

        nombre_archivo = f'libro_mayor_{año}_{mes}_{cuenta}.xlsx'
        return send_file(
            output,
            download_name=nombre_archivo,
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        print(f"Error al generar el libro mayor: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conexion:
            cursor.close()
            conexion.close()

