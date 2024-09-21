from decouple import config 
import psycopg2

def obtener_conexion():
    return psycopg2.connect(
        host=config('POSTGRES_HOST'),
        port=config('POSTGRES_PORT'),
        user=config('POSTGRES_USER'),
        password=config('POSTGRES_PASSWORD'),
        database=config('POSTGRES_DB')
    )

def consultar_hora():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT NOW();")
    hora_actual = cursor.fetchone()[0]
    cursor.close()
    conexion.close()
    return hora_actual
hora_actual = consultar_hora()
print("La hora actual es:", hora_actual)



