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
                SET estado = 'FACTURADO'
                WHERE COT = %s;
            """
            insertar_factura = """
            INSERT INTO facturas (NFAC, id_venta, fecha_emision)
            VALUES (%s, %s, %s);
            """
            insertar_factura_detalle = """
            INSERT INTO factura_detalle (NFAC, id_producto, cantidad)
            VALUES (%s, %s, %s);
            """
            db.execute(actualizar, (datos_json["COT"],))
            if db.rowcount != 1:
                db.connection.rollback()
                print(f"COT {datos_json['COT']} no encontrado.")
                return json.dumps({
                    "estado": "error",
                    "mensaje": "Error al encontrar cotización"
                })
            for factura in datos_json["facturas"]:
                db.execute(insertar_factura, (factura["numero_factura"], datos_json["COT"], factura["fecha"]))
                for producto in factura["productos"]:
                    db.execute(insertar_factura_detalle, (factura["numero_factura"], producto["id_producto"], producto["cantidad"]))
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

def actualizar_excep(db, datos_json):
    print("Atendiendo peticion de actualizacion excepcional...")
    try:
        verify_user = """
        SELECT rol
        FROM usuarios
        WHERE rut = %s;
        """
        db.execute(verify_user, (datos_json["user"],))
        resultado = db.fetchone()
        rol = resultado[0]
        if rol != "Dueño":
            print("No tiene rol permitido para esta acción")
            return json.dumps({
                "estado": "error",
                "mensaje": "No cumple con rol necesario para esta acción"
            })
        #   No se bien como seguir esto
    except Exception as e:
        print("Error al atender petición")
        db.connection.rollback()
        return json.dumps({
            "estado": "error",
            "mensaje": "Error interno del servidor"
        })