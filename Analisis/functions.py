import json
import os
import psycopg2
from psycopg2 import Error

def dbconnect():
    try:
        # Obtener credenciales
        connection = psycopg2.connect(
            host=os.environ.get("DB_HOST", "db"),
            database=os.environ.get("DB_NAME", "db"),
            user=os.environ.get("DB_USER", "admin"),
            password=os.environ.get("DB_PASS", "colocolo"),
            port="5432"
        )
        cursor = connection.cursor()
        print("Conexion exitosa")
        return cursor
    except (Exception, Error) as error:
        print("Error al conectar con postgreSQL:", error)
        return None

def grafico_cliente(db, datos_json):
    print(f"Obteniendo datos para graficos de clientes...")

def grafico_productos(db, datos_json):
    print(f"Obteniendo datos para grafico de productos desde {datos_json['fecha_inicio']} hasta {datos_json['fecha_fin']}...")
    query = """
        SELECT p.id, p.nombre, SUM(vd.cantidad) as total_vendido
        FROM productos as p
        JOIN venta_detalle as vd ON p.id = vd.id_producto
        JOIN ventas as v ON vd.id_venta = v.COT
        WHERE v.fecha_cot BETWEEN %s AND %s
        GROUP BY p.id, p.nombre
        ORDER BY total_vendido DESC;
    """
    try:
        db.execute(query, (datos_json["fecha_inicio"], datos_json["fecha_fin"]))
        resultado = db.fetchall()
        datos_grafico = []
        for fila in resultado:
            datos_grafico.append({
                "id_producto": fila[0],
                "nombre": fila[1],
                "cantidad": int(fila[2]) if fila[2] else 0
            })
        print("Datos obtenidos correctamente")
        return json.dumps({
            "estado": "ok",
            "mensaje": "Datos obtenidos correctamente",
            "datos": datos_grafico
        })
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return json.dumps({
            "estado": "error",
            "mensaje": "Error interno del servidor"
        })