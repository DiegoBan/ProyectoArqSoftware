from soa_lib import connect_to_bus, send_message, receive_message
from functions import dbconnect, crear_usuario, iniciar_sesion, modificar_rol
import json

sock = connect_to_bus()

try:
    # Registro inicial (sinit)
    print("Registrando servicio 'usuar'...")
    send_message(sock, "sinit", "usuar")    #   Nombre de servicio en bus usuar
    
    # Procesar respuesta del sinit
    init_data = receive_message(sock)
    print(f"Confirmación de bus recibida: {init_data!r}")
    print("Servicio listo para recibir transacciones.\n")
    
    # Conectarse a la base de datos
    print("Conectando con base de datos...")
    db = dbconnect()
    if db is None:
        exit()
    # Bucle principal de trabajo
    print("Entrando en bucle principal de trabajo...")
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
            case "crear_usuario":
                datos_json = crear_usuario(db, datos_json)
                send_message(sock, "front", datos_json)
            case "iniciar_sesion":
                datos_json = iniciar_sesion(db, datos_json)
                send_message(sock, "front", datos_json) #   "front" es frontend, debe cambiar según como se programe el front
            case "modificar_rol":
                datos_json = modificar_rol(db, datos_json)
                send_message(sock, "front", datos_json)

except Exception as e:
    print(f"Error en el servicio: {e}")
finally:
    print('Cerrando socket del servicio')
    sock.close()
