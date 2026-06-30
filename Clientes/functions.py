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
    # FIX: tabla "cliente" no existe, la tabla real es "clientes" (plural).
    # FIX: el frontend nunca manda "id" (no lo conoce), pero sí manda
    # "rut_empresa" que es UNIQUE en la tabla, así que filtramos por ahí.
    query = """
        UPDATE clientes
        SET nombre=%s
        WHERE rut_empresa=%s;
    """
    
    try:
        db.execute(verify)
        admins = db.fetchall()
        admins = [fila[0] for fila in admins]
        # FIX: el frontend manda "user_rut", no "user". Antes esto lanzaba
        # KeyError siempre y caía directo al except con un error genérico.
        if datos_json.get("user_rut") not in admins:
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
            
            db.execute(query, (nombre, rut_empresa))
            db.connection.commit()
            print('Query enviada a base de datos, esperando respuesta...')
            
            return json.dumps({
                "estado": "ok",
                "mensaje": "Actualización exitosa",
                "accion": "actualizar_cliente",
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
    
    # FIX: tabla "cliente" no existe, la tabla real es "clientes" (plural).
    query = """
        INSERT INTO clientes (nombre, rut_empresa)
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
        # FIX: el frontend manda "user_rut", no "user".
        if datos_json.get("user_rut") not in admins:
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
                "accion": "crear_cliente",
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
    
def eliminar_cliente(db, datos_json):
    # NUEVO: no existía esta funcionalidad. Mismo patrón de verificación admin
    # que actualizar_cliente/registrar_cliente, e identifica al cliente por
    # rut_empresa (UNIQUE en la tabla), igual que actualizar_cliente.
    print("<--- Eliminando cliente --->")
    print("Cliente a eliminar:", datos_json)

    verify = """
        SELECT rut FROM usuarios 
        WHERE rol = 'admin';
    """
    query = """
        DELETE FROM clientes
        WHERE rut_empresa=%s;
    """

    try:
        db.execute(verify)
        admins = db.fetchall()
        admins = [fila[0] for fila in admins]
        if datos_json.get("user_rut") not in admins:
            return json.dumps({
                "estado": "error",
                "tipo": "Usuario no verificado",
                "mensaje": "No se pudo eliminar el cliente porque el usuario no es administrador.",
                "detalles": {
                    "User": "El usuario no es administrador"
                }
            })

        rut_empresa = datos_json.get("rut_empresa")
        db.execute(query, (rut_empresa,))
        if db.rowcount == 0:
            return json.dumps({
                "estado": "error",
                "mensaje": "Cliente no encontrado"
            })

        db.connection.commit()
        print("Cliente eliminado con éxito")
        return json.dumps({
            "estado": "ok",
            "mensaje": "Cliente eliminado",
            "accion": "eliminar_cliente",
            "detalles": {
                "rut_empresa": rut_empresa
            }
        })
    except Exception as e:
        db.connection.rollback()
        print(f"Error al eliminar cliente: {e}")
        return json.dumps({
            "estado": "error",
            "mensaje": "error interno del servidor"
        })