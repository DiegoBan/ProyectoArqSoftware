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
    try:
        start_date = f"datos_json['fecha_inicio']-01"
        fin_anio, fin_mes = map(int, datos_json['fecha_fin'].split('-'))
        if fin_anio == 12:
            sig_anio = fin_anio+1
            sig_mes = 1
        else:
            sig_anio = fin_anio
            sig_mes = sig_mes+1
        end_date = f"{sig_anio}-{sig_mes:02d}-01"
        formato_fecha = 'YYYY-MM' if datos_json['agrupar'] == "mes" else 'YYYY'

        query = f"""
            WITH VentaTotales AS (
                SELECT
                    v.COT,
                    v.id_cliente,
                    v.fecha_cot,
                    SUM(vd.cantidad * vd.precio_unitario) as total_venta
                FROM ventas as v
                JOIN venta_detalle as vd ON v.COT = vd.id_venta
                WHERE v.fecha_cot >= %s AND v.fecha_cot < %s
                GROUP BY v.COT, v.id_cliente, v.fecha_cot
            ),
            FacturasPendientes AS (
                SELECT DISTINCT id_venta
                FROM facturas
                WHERE estado = 'PENDIENTE'
            )
            SELECT
                c.id as id_cliente,
                c.nombre as nombre_cliente,
                TO_CHAR(vt.fecha_cot, '{formato_fecha}') as periodo,
                SUM(vt.total_venta) as volumen_ventas,
                SUM(CASE WHEN fp.id_venta IS NOT NULL THEN vt.total_venta ELSE 0 END) as deuda_activa
            FROM clientes as c
            JOIN VentaTotales as vt ON c.id = vt.id_cliente
            LEFT JOIN FacturasPendientes as fp ON vt.COT = fp.id_venta
            GROUP BY c.id, c.nombre, periodo
            ORDER BY c.nombre, periodo;
        """

        db.execute(query, (start_date, end_date))
        resultados = db.fetchall()
        clientes_agrupados = {}
        for fila in resultados:
            id_cliente = fila[0]
            nombre_cliente = fila[1]
            periodo = fila[2]
            volumen = int(fila[3]) if fila[3] else 0
            deuda = int(fila[4]) if fila[4] else 0
            if id_cliente not in clientes_agrupados:
                clientes_agrupados[id_cliente] = {
                    "id_cliente": id_cliente,
                    "nombre_cliente": nombre_cliente,
                    "datos": []
                }
            clientes_agrupados[id_cliente]["datos"].append({
                "periodo": periodo,
                "volumen_ventas": volumen,
                "deuda_activa": deuda
            })
        lista_final = list(clientes_agrupados.values())
        return json.dumps({
            "estado": "ok",
            "mensaje": "Datos generados correctamente",
            "datos": lista_final
        })
    except Exception as e:
        print(f"Error al obtener datos {e}")
        return json.dumps({
            "estado": "error",
            "mensaje": "Error interno del servidor"
        })

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