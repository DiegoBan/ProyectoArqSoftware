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
    
def obtener_productos(db):
    print("<--- Obteniendo productos --->")
    query = """
        SELECT * FROM productos;
    """
    try:
        db.execute(query)
        clientes = db.fetchall()
        if not clientes:
            print("No existen productos")
            return json.dumps({
                "estado": "error",
                "mensaje": "No existen productos"
            })
        else:
            print("Se han obtenido productos")
            
            nombres_columnas = [columna[0] for columna in db.description]
            productos_formateados = [dict(zip(nombres_columnas, filas)) for filas in clientes]
            
            return json.dumps({
                "estado": "ok",
                "mensaje": "Clientes obtenidos",
                "productos": productos_formateados
            })
    except Exception as e:
        print(f"Error en la obtención de productos: {e}")
        return json.dumps({
            "estado": "error",
            "mensaje": "error interno del servidor"
        })
        
def crear_producto(db, datos_json):
    print("<--- Creando producto --->")
    print("Producto a crear:", datos_json)
    
    query = """
        INSERT INTO producto (nombre, familia, subfamilia, descripcion, PN, serie)
        VALUES (%s, %s, %s, %s, %s, %s);
    """
    verify = """
        SELECT rut FROM usuarios 
        WHERE rol = 'admin';
    """
    
    try:
        db.execute(verify)
        admins = db.fetchall()
        admins = [fila[0] for fila in admins]
        if datos_json["user"] not in admins: # Los usuarios que se tienen que verificar se tiene que arreglar mas adelante
            return json.dumps({
                "estado": "error",
                "tipo": "Usuario no verificado",
                "mensaje": "No se pudo crear producto porque el usuario no es administrador.",
                "detalles": {
                    "User": "El usuario no es administrador"
                }
            })
        else:
            nombre = datos_json.get("nombre")
            familia = datos_json.get("familia")
            subfamilia = datos_json.get("subfamilia")
            descripcion = datos_json.get("descripcion")
            PN = datos_json.get("PN")
            serie = datos_json.get("serie")
            
            db.execute(query, (nombre, familia, subfamilia, descripcion, PN, serie))
            db.connection.commit()
            print('Query enviada a base de datos, esperando respuesta...')
            
            return json.dumps({
                "estado": "ok",
                "mensaje": "Registro exitoso",
                "detalles": {
                    "nombre": nombre,
                    "familia": familia,
                    "subfamilia": subfamilia,
                    "descripcion": descripcion,
                    "PN": PN,
                    "serie": serie,
                }
            })
    except Exception as e:
        print(f"Error en la creación de producto: {e}")
        return json.dumps({
            "estado": "error",
            "mensaje": "error interno del servidor"
        })
    