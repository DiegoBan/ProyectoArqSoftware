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

def crear_usuario(db, datos_json):
    print(f"Creando usuario")
    print('Datos a enviar:', json.dumps(datos_json))
    """
    # <--- Verificaciones --->
    if datos_json["user"] != 'pepito': # Los usuarios que se tienen que verificar se tiene que arreglar mas adelante
        respuesta_error = {
            "estado": "error",
            "tipo": "Usuario no verificado",
            "mensaje": "No se pudo crear el usuario porque el usuario no es administrador.",
            "detalles": {
                "User": "El usuario no esta verificado"
            }
        }
        send_message(sock, "Usuario", json.dumps(respuesta_error))
                
    # <--- Envio de query a BD --->
    rut = datos_json.get("rut")
    email = datos_json.get("email")
    contrasena = datos_json.get("password_hash")
    nombre = datos_json.get("nombre")
    apellido = datos_json.get("apellido")
    rol = datos_json.get("rol")
    telefono = datos_json.get("telefono")
    fecha_nacimiento = datos_json.get("Fecha_nacimiento")
                
    mensaje_bd = {
        'accion': 'crear_usuario',
        'query': 'insert into Usuarios (rut, email, password_hash, nombre, apellido, rol, telefono, Fecha_nacimiento) values (%s,%s,%s,%s,%s,%s,%s,%s);',
        'values': [rut, email, contrasena, nombre, apellido, rol, telefono, fecha_nacimiento]
        }
    send_message(sock, 'db', json.dumps(mensaje_bd))
    print('Query enviada a base de datos, esperando respuesta...')
    """

def iniciar_sesion(db, datos_json):
    print("Intento de login...")
    query = """
        SELECT id, password_hash, nombre, rol
        FROM usuarios
        WHERE email = %s;
    """
    try:
        db.execute(query, (datos_json["email"],))
        usuario = db.fetchone()
        if not usuario:
            print("login error: Usuario no encontrado")
            return json.dumps({
                "estado": "error",
                "mensaje": "Usuario no encontrado"
            })
        id_user, hash_user, nombre_user, rol_user = usuario
        if hash_user == datos_json["password_hash"]:
            print(f"Login exitoso para usuario ID: {id_user}")
            return json.dumps({
                "estado": "ok",
                "mensaje": "autenticación exitosa",
                "usuario": {
                    "id": id_user,
                    "nombre": nombre_user,
                    "rol": int(rol_user)
                }
            })
        else:
            print("Intento del login fallido: password incorrecta")
            return json.dumps({
                "estado": "error",
                "mensaje": "password incorrecta"
            })
    except Exception as e:
        print(f"Error en consulta de login: {e}")
        return json.dumps({
            "estado": "error",
            "mensaje": "error interno del servidor"
        })