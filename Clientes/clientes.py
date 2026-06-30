from soa_lib import connect_to_bus, send_message, receive_message
from functions import dbconnect, obtener_clientes, actualizar_cliente, registrar_cliente, eliminar_cliente
import json

sock = connect_to_bus()

try:
    # Registro inicial (sinit)
    print("Registrando servicio 'clien'...")
    send_message(sock, "sinit", "clien")    #   Nombre de servicio en bus usuar
    
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
            case "obtener_clientes":
                respuesta_json = obtener_clientes(db)
                send_message(sock, "front", respuesta_json)
            case "actualizar_cliente":
                respuesta_json = actualizar_cliente(db, datos_json)
                send_message(sock, "front", respuesta_json)
            case "crear_cliente":
                # FIX: el case anterior decía "regitrar_cliente" (typo) y nunca
                # matcheaba con lo que manda el frontend ("crear_cliente"),
                # por eso el servicio nunca respondía y la UI quedaba pegada.
                respuesta_json = registrar_cliente(db, datos_json)
                send_message(sock, "front", respuesta_json)
            case "eliminar_cliente":
                # NUEVO: funcionalidad solicitada, no existía en el backend.
                respuesta_json = eliminar_cliente(db, datos_json)
                send_message(sock, "front", respuesta_json)

except Exception as e:
    print(f"Error en el servicio: {e}")
finally:
    print('Cerrando socket del servicio')
    sock.close()