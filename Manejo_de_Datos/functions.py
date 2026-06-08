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
    
def crear_cotizacion(db, datos_json):
    print(f"Creando cotizacion {datos_json['COT']}...")
    insert_ventas = """
        INSERT INTO ventas (COT, id_cliente, fecha_cot)
        VALUES (%s, %s, %s);
    """
    insert_detalle = """
        INSERT INTO venta_detalle (id_venta, id_producto, cantidad, precio_unitario)
        VALUES (%s, %s, %s, %s);
    """
    try:
        db.execute(insert_ventas, (datos_json["COT"], datos_json["id_cliente"], datos_json["fecha_cot"]))
        for producto in datos_json["productos"]:
            db.execute(insert_detalle, (datos_json["COT"], producto["id_producto"], producto["cantidad"], producto["precio_unitario"]))
        db.connection.commit()
        print("Cotizacion creada")
        return json.dumps({
            "estado": "ok",
            "mensaje": "Cotización creada correctamente"
        })
    except Exception as e:
        print(f"Error al crear corizacion: {e}")
        db.connection.rollback()
        return json.dumps({
            "estado": "error",
            "mensaje": "Error interno del servidor"
        })
    
def actualizar_cotizacion(db, datos_json):
    print("Atendiendo petición de actualización...")
    try:
        if "orden_de_compra" in datos_json: #   Actualizar desde COTIZADO a OCO
            print(f"Actualizando cotizacion {datos_json['COT']} COTIZADO a OCO...")
            actualizar = """
                UPDATE ventas
                SET estado = 'OCO',
                orden_de_compra = %s,
                fecha_oco = %s,
                nota_de_venta = %s
                WHERE COT = %s;
            """
            db.execute(actualizar, (datos_json["orden_de_compra"], datos_json["fecha_oco"], datos_json["nota_de_venta"], datos_json["COT"]))
            if db.rowcount == 1:
                db.connection.commit()
                print("Actualizado correctamente")
                return json.dumps({
                "estado": "ok",
                "mensaje": "Correctamente actualizado desde COTIZADO a OCO"
                })
            print("COT no encontrado, ninguna fila afectada")
            db.connection.rollback()
            return json.dumps({
                "estado": "error",
                "mensaje": "Error al encontrar COT"
            })
        else:   #   Actualizar desde OCO a FACTURADO
            print(f"Actualizando cotizacion {datos_json['COT']} OCO a FACTURADO...")
            actualizar = """
                UPDATE ventas
                SET estado = 'FACTURADO',
                numero_factura = %s,
                fecha_factura = %s,
                estado_factura = 'PENDIENTE'
                WHERE COT = %s;
            """
            db.execute(actualizar, (datos_json['numero_factura'], datos_json['fecha_factura'], datos_json['COT']))
            if db.rowcount != 1:
                db.rollback()
                print(f"COT {datos_json['COT']} no encontrado")
                return json.dumps({
                    "estado": "error",
                    "mensaje": "COT no encontrado correctamente"
                })
            db.connection.commit()
            print("Actualizado correctamente")
            return json.dumps({
                "estado": "ok",
                "mensaje": "Correctamente actualizado desde OCO a FACTURADO"
            })
    except Exception as e:
        print("Error al atender petición")
        db.connection.rollback()
        return json.dumps({
            "estado": "error",
            "mensaje": "Error interno del servidor"
        })
        
def ver_detalles(db):
    print("<-- Ver detalles de todas las cotizaciones --->")
    query = """
        SELECT COT fecha_creacion, estado, fecha_cot, orden_de_compra, fecha_oco, nota_de_venta, numero_factura, fecha_factura, estado_factura, clientes.nombre as nombre_cliente, venta_detalle.cantidad, venta_detalle.precio_unitario, productos.nombre, productos.familia, productos.subfamilia, productos.descripcion, productos.PN, productos.serie, guia_detalle.numero_guia, guia_detalle.cantidad as cantidad_guia
        FROM ventas
        JOIN clientes ON ventas.id_cliente = clientes.id
        JOIN venta_detalle ON ventas.COT = venta_detalle.id_venta
        JOIN productos ON productos.id = venta_detalle.id_producto
        LEFT JOIN guia_despacho ON guia_despacho.id_venta = ventas.COT
        LEFT JOIN guia_detalle ON guia_detalle.numero_guia = guia_despacho.numero_guia 
            AND guia_detalle.id_producto = venta_detalle.id_producto
        ORDER BY ventas.COT DESC;
    """
    try:
        db.execute(query)
        filas = db.fetchall()
        
        columnas = [desc[0] for desc in db.description]
        
        detalles_formateados = []
        for fila in filas:
            fila_dict = dict(zip(columnas, fila))
            
            for clave, valor in fila_dict.items():
                if hasattr(valor, 'isoformat'):
                    fila_dict[clave] = valor.isoformat()
            detalles_formateados.append(fila_dict)
        print("Se obtuvieron bien los resultados:", len(detalles_formateados), "filas")
        
        return json.dumps({
            "estado": "ok",
            "mensaje": "Detalles de cotizaciones obtenidos",
            "detalles": detalles_formateados
        })
        
    except Exception as e:
        print(f"Error al obtener detalle de venta: {e}")
        return json.dumps({
            "estado": "error",
            "mensaje": "Error interno del servidor"
        })