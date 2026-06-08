import json
import os
from decimal import Decimal
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
    
def obtener_clientes(db):
    print("<--- Obteniendo usuarios --->")
    query = """
        SELECT * FROM clientes;
    """
    try:
        db.execute(query)
        clientes = db.fetchall()
        if not clientes:
            print("No existen Clientes")
            return json.dumps({
                "estado": "error",
                "mensaje": "No existen clientes"
            })
        else:
            print("Se han obtenido clientes")
            
            nombres_columnas = [columna[0] for columna in db.description]
            clientes_formateados = []
            
            for fila in clientes:
                # Unir columnas con valores
                fila_dict = dict(zip(nombres_columnas, fila))
                
                # Buscar datos rebeldes (como el RUT) y convertirlos a tipos que JSON entienda
                for clave, valor in fila_dict.items():
                    if isinstance(valor, Decimal):
                        fila_dict[clave] = int(valor) # Convertimos el Decimal a Entero
                        
                clientes_formateados.append(fila_dict)
            
            print(clientes_formateados)
            return json.dumps({
                "estado": "ok",
                "mensaje": "Clientes obtenidos",
                "clientes": clientes_formateados
            })
    except Exception as e:
        print(f"Error en la obtención de clientes: {e}")
        return json.dumps({
            "estado": "error",
            "mensaje": "error interno del servidor"
        })
    
def actualizar_cliente(db, datos_json):
    print("<--- Actualizando cliente --->")
    print("Datos a actualizar:", datos_json)
    
    verify = """
        SELECT rut FROM usuarios 
        WHERE rol = 'admin';
    """
    query = """
        UPDATE cliente
        SET nombre=%s, rut_empresa=%s
        WHERE id=%s;
    """
    
    try:
        db.execute(verify)
        admins = db.fetchall()
        admins = [fila[0] for fila in admins]
        if datos_json["user"] not in admins: # Los usuarios que se tienen que verificar se tiene que arreglar mas adelante
            return json.dumps({
                "estado": "error",
                "tipo": "Usuario no verificado",
                "mensaje": "No se pudo actualizar el cliente porque el usuario no es administrador.",
                "detalles": {
                    "User": "El usuario no es administrador"
                }
            })
        else:
            nombre = datos_json.get("nombre")
            rut_empresa = datos_json.get("rut_empresa")
            id = datos_json.get("id")
            
            db.execute(query, (nombre, rut_empresa, id))
            db.connection.commit()
            print('Query enviada a base de datos, esperando respuesta...')
            
            return json.dumps({
                "estado": "ok",
                "mensaje": "Actualización exitosa",
                "detalles": {
                    "nombre": nombre,
                    "rut_empresa": rut_empresa
                }
            })
    except Exception as e:
        print(f"Error en actualización de cliente: {e}")
        return json.dumps({
            "estado": "error",
            "mensaje": "error interno del servidor"
        })
        
def registrar_cliente(db, datos_json):
    print("<--- Realizando registro --->")
    print("Cliente a registrar:", datos_json)
    
    query = """
        INSERT INTO cliente (nombre, rut_empresa)
        VALUES (%s, %s);
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
                "mensaje": "No se pudo registrar el cliente porque el usuario no es administrador.",
                "detalles": {
                    "User": "El usuario no es administrador"
                }
            })
        else:
            nombre = datos_json.get("nombre")
            rut_empresa = datos_json.get("rut_empresa")
            
            db.execute(query, (nombre, rut_empresa))
            db.connection.commit()
            print('Query enviada a base de datos, esperando respuesta...')
            
            return json.dumps({
                "estado": "ok",
                "mensaje": "Registro exitoso",
                "detalles": {
                    "nombre": nombre,
                    "rut_empresa": rut_empresa
                }
            })
    except Exception as e:
        print(f"Error en el registro del cliente: {e}")
        return json.dumps({
            "estado": "error",
            "mensaje": "error interno del servidor"
        })
    