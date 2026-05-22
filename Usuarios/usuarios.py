from soa_lib import connect_to_bus, send_message, receive_message
import time
import json

sock = connect_to_bus()

try:
    # 1. Registro inicial (sinit)
    print("Registrando servicio 'Usuarios'...")
    send_message(sock, "Usuarios", "servi")
    
    # 2. Procesar respuesta del sinit
    init_data = receive_message(sock)
    print(f"Confirmación de bus recibida: {init_data!r}")
    print("Servicio listo para recibir transacciones.\n")
    
    # 3. Bucle principal de trabajo
    while True:
        data = receive_message(sock)
        if not data:
            print("Conexión cerrada por el bus.")
            break
        
        mensaje = data[5:].decode()
        datos_json = json.loads(mensaje)
        
        accion = datos_json.get("accion")
        print(f"Realizando acción: '{accion}'")
        match accion:
            case "crear":
                print(f"Creando usuario con datos {mensaje}")
                print('Datos a enviar:', datos_json.dumps())
                # <--- Verificaciones --->
                if datos_json.user != 'pepito': # Los usuarios que se tienen que verificar se tiene que arreglar mas adelante
                    respuesta_error = {
                        "estado": "error",
                        "tipo": "Usuario no verificado",
                        "mensaje": "No se pudo crear el usuario porque el usuario no es administrador.",
                        "detalles": {
                            "User": "El usuario no esta verificado"
                        }
                    }
                    send_message(sock, "Usuario", json.dumps(respuesta_error))
                    continue
                
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
                
                respuesta_db = receive_message(sock)
                
                
                
            case "Modificar":
                print(f"Modificando emnpleado con datos {mensaje}")
    
            
        # Extraer el payload (salta los 5 caracteres del nombre del servicio)
        print(f"Mensaje recibido del cliente: '{mensaje}'")
        try:
            segundos = int(mensaje)
            print(f"Simulando trabajo: durmiendo {segundos}s...")
            
            time.sleep(segundos)
            
            # Responder al cliente a través del bus
            send_message(sock, "Usuarios", "OK")
            print("Respuesta 'OK' enviada.")
            
        except ValueError:
            print(f"Error: '{mensaje}' no es un número válido.")
            send_message(sock, "Usuarios", "Error: Formato incorrecto")

except Exception as e:
    print(f"Error en el servicio: {e}")
finally:
    print('Cerrando socket del servicio')
    sock.close()
