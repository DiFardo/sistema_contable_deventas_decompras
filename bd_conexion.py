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