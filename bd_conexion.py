from decouple import config
import psycopg2

def obtener_conexion():
    return psycopg2.connect(
        host=config('POSTGRES_HOST', default='pg-servercontable-calidad-2024.d.aivencloud.com'),
        port=config('POSTGRES_PORT', default='26134'),
        user=config('POSTGRES_USER', default='avnadmin'),
        password=config('POSTGRES_PASSWORD', default='AVNS_8q6hd4Rhe2XMjRIpU_G'),
        database=config('POSTGRES_DB', default='servidor_sistema_contable')
    )
