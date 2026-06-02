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
    print(f"<--- Creando usuario --->")
    print('Datos a enviar:', json.dumps(datos_json))
    
    query = """
        INSERT INTO usuarios (rut, email, password_hash, nombre, apellido, rol, telefono, Fecha_nacimiento) 
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s);
    """
    verify = """
        SELECT rut FROM usuarios 
        WHERE rol = 'admin';
    """
    
    try :
        # <--- Verificaciones --->
        db.execute(verify)
        admins = db.fetchall()
        admins = [fila[0] for fila in admins]
        if datos_json["user"] not in admins: 
            return json.dumps({
                "estado": "error",
                "tipo": "Usuario no verificado",
                "mensaje": "No se pudo crear el usuario porque el usuario no es administrador.",
                "detalles": {
                    "User": "El usuario no es administrador"
                }
            })
        else:
            # <--- Envio de query a BD --->
            rut = datos_json.get("rut")
            email = datos_json.get("email")
            contrasena = datos_json.get("password_hash")
            nombre = datos_json.get("nombre")
            apellido = datos_json.get("apellido")
            rol = datos_json.get("rol")
            telefono = datos_json.get("telefono")
            fecha_nacimiento = datos_json.get("Fecha_nacimiento")
        
            db.execute(query, (rut, email, contrasena, nombre, apellido, rol, telefono, fecha_nacimiento))
            db.connection.commit()
            print('Query enviada a base de datos, esperando respuesta...')
            
            return json.dumps({
                "estado": "ok",
                "mensaje": "Creación exitosa",
                "detalles": {
                    "rut": rut,
                    "email": email,
                    "contrasena": contrasena,
                    "nombre": nombre,
                    "apellido": apellido,
                    "rol": rol,
                    "telefono": telefono,
                    "fecha_nacimiento": fecha_nacimiento
                }
            })
    except Exception as e:
        print(f"Error en creación de usuario: {e}")
        return json.dumps({
            "estado": "error",
            "mensaje": "error interno del servidor"
        })

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
                    "rol": rol_user
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

def modificar_rol(db, datos_json):
    print("Modificando rol...")
    query1 = """SELECT rol FROM usuarios WHERE id = %s;"""
    query2 = """
        UPDATE usuarios
        SET rol = %s
        WHERE id = %s;
    """
    try:
        db.execute(query1, (datos_json["modificador_id"],))
        modificador = db.fetchone()
        if not modificador: # Usuario modificador no existe
            print("Modificacion error: usuario modificador no encontrado")
            return json.dumps({
                "estado": "error",
                "mensaje": "Usuario modificador no encontrado"
            })
        rol_modificador = modificador[0]
        if rol_modificador != "admin":  
            print("Modificacion rechazada: usuario no es admin")
            return json.dumps({
                "estado": "error",
                "mensaje": "Usuario no es admin"
            })
        db.execute(query2, (datos_json["nuevo_rol"], datos_json["modificar_id"]))
        if db.rowcount == 0:
            print("Modificacion error: Usuario a modificar no existe")
            return json.dumps({
                "estado": "error",
                "mensaje": "Usuario a modificar no existe"
            })
        db.connection.commit() 
        print("Modificacion de rol con exito")
        return json.dumps({
            "estado": "ok",
            "mensaje": "rol modificado"
        })
    except Exception as e:
        db.connection.rollback()    #   En caso de que la transacción falle, eliminar datos erroneos de base de datos
        print(f"Error al modificar rol: {e}") 
        return json.dumps({
            "estado": "error",
            "mensaje": "error interno del servidor"
        })