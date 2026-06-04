from soa_lib import connect_to_bus, send_message, receive_message
from functions import dbconnect, obtener_productos, crear_producto
import json

sock = connect_to_bus()

try:
    # Registro inicial (sinit)
    print("Registrando servicio 'produ'...")
    send_message(sock, "sinit", "produ")    #   Nombre de servicio en bus usuar
    
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
            case "obtener_productos":
                datos_json = obtener_productos(db)
                send_message(sock, "front", datos_json)
            case "crear_producto":
                datos_json = crear_producto(db, datos_json)
                send_message(sock, "front", datos_json)

except Exception as e:
    print(f"Error en el servicio: {e}")
finally:
    print('Cerrando socket del servicio')
    sock.close()
