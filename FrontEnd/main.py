import flet as ft
import json
from soa_lib import connect_to_bus, send_message, receive_message

from vistas.crearuser import vista_crear_usuario
from vistas.login import vista_login
from vistas.home import vista_dashboard
from vistas.productos import vista_productos
from vistas.confirmar_producto import vista_confirmar_producto
from vistas.ventas import vista_dashboard_ventas
from vistas.nueva_cotizacion import vista_nueva_cotizacion
from vistas.historial_ventas import vista_estado_cotizaciones
from vistas.clientes import vista_clientes
from vistas.empleados import vista_empleados


def main(page: ft.Page):
    page.title = "Frontend - Proyecto Arquitectura de Software"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

    # 1. Conexión al Bus
    try:
        sock = connect_to_bus()
        send_message(sock, "sinit", "front")
    except Exception as e:
        page.add(ft.Text(f"Error crítico conectando al bus: {e}", color=ft.Colors.RED))
        return

    # 2. Enrutamiento — LAZY: solo construye la vista solicitada.
    # ANTES: el dict evaluaba TODAS las vistas al construirse, ejecutando los
    # send_message de clientes/empleados/ventas aunque estuvieras en el login,
    # llenando el buffer TCP con mensajes basura antes de autenticarse.
    def cambiar_vista(nombre_vista):
        page.controls.clear()
        constructores = {
            "login":               lambda: vista_login(page, sock),
            "crear_usuario":       lambda: vista_crear_usuario(page, sock, cambiar_vista),
            "dashboard":           lambda: vista_dashboard(page, sock, cambiar_vista),
            "productos":           lambda: vista_productos(page, sock, cambiar_vista),
            "confirmar_producto":  lambda: vista_confirmar_producto(page, sock, cambiar_vista),
            "ventas":              lambda: vista_dashboard_ventas(page, sock, cambiar_vista),
            "nueva_cotizacion":    lambda: vista_nueva_cotizacion(page, sock, cambiar_vista),
            "estado_cotizaciones": lambda: vista_estado_cotizaciones(page, sock, cambiar_vista),
            "clientes":            lambda: vista_clientes(page, sock, cambiar_vista),
            "empleados":           lambda: vista_empleados(page, sock, cambiar_vista),
        }
        constructor = constructores.get(nombre_vista)
        if constructor:
            page.add(constructor())
        page.update()

    # Helper: mostrar snackbar y siempre rehabilitar la UI
    def mostrar_snackbar(mensaje, color):
        alerta = ft.SnackBar(ft.Text(mensaje), bgcolor=color)
        page.overlay.append(alerta)
        alerta.open = True
        if page.controls:
            page.controls[0].disabled = False
        page.update()

    # 3. Hilo de Escucha con buffer acumulador propio.
    # PROBLEMA: soa_lib.receive_message usa recv() que no respeta límites de mensaje
    # en TCP. Si el bus concatena varios mensajes en el buffer (como se ve en el log:
    # <00031venta...00053usuar...00035clien...>), recv(5) puede leer a la mitad
    # de un mensaje anterior y corromper el parse del JSON → pantalla pegada.
    # SOLUCIÓN: acumular bytes aquí y extraer mensajes según el protocolo [5 longitud][N contenido].
    def escuchar_bus():
        tcp_buffer = b''

        def leer_exacto(n):
            nonlocal tcp_buffer
            while len(tcp_buffer) < n:
                chunk = sock.recv(4096)
                if not chunk:
                    raise ConnectionError("Bus cerró la conexión")
                tcp_buffer += chunk
            resultado = tcp_buffer[:n]
            tcp_buffer = tcp_buffer[n:]
            return resultado

        while True:
            try:
                raw_len = leer_exacto(5)
                n = int(raw_len)
                data = leer_exacto(n)

                # Protocolo: [5 chars servicio destino][payload JSON]
                mensaje_crudo = data[5:].decode()
                respuesta = json.loads(mensaje_crudo)

                if respuesta.get("estado") == "ok":

                    if "usuario" in respuesta:
                        # Login exitoso
                        usuario = respuesta.get("usuario", {})
                        page.session.store.set("rol", str(usuario.get("rol")))
                        page.session.store.set("rut", usuario.get("rut"))
                        page.session.store.set("nombre", usuario.get("nombre"))
                        cambiar_vista("dashboard")

                    elif "usuarios" in respuesta:
                        import vistas.empleados as ve
                        ve.LISTA_EMPLEADOS = respuesta["usuarios"]
                        cambiar_vista("empleados")

                    elif "clientes" in respuesta:
                        import vistas.clientes as vc
                        vc.LISTA_CLIENTES = respuesta["clientes"]
                        cambiar_vista("clientes")

                    else:
                        # El servicio responde {"estado":"ok","mensaje":"..."} SIN campo "accion".
                        # Para saber qué refrescar usamos el request que enviamos, no la respuesta.
                        # Como no tenemos acceso directo al request aquí, refrescamos ambas listas
                        # de forma segura según qué vista está activa, o simplemente rehabilitamos
                        # la UI y dejamos que el usuario navegue. Para acciones que sí devuelven
                        # "accion" en la respuesta mantenemos el comportamiento anterior.
                        accion_resp = respuesta.get("accion")
                        if accion_resp == "actualizar_rol":
                            send_message(sock, "usuar", json.dumps({
                                "accion": "obtener_usuarios",
                                "user_rut": page.session.store.get("rut")
                            }))
                        elif accion_resp in ("crear_cliente", "actualizar_cliente"):
                            send_message(sock, "clien", json.dumps({
                                "accion": "obtener_clientes",
                                "user_rut": page.session.store.get("rut")
                            }))
                        else:
                            # Respuesta genérica sin "accion": solo rehabilitar UI
                            if page.controls:
                                page.controls[0].disabled = False
                        mostrar_snackbar(respuesta.get("mensaje", "Éxito"), ft.Colors.GREEN_700)

                else:
                    mostrar_snackbar(respuesta.get("mensaje", "Error desconocido"), ft.Colors.RED_700)

            except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as ex:
                print(f"[escuchar_bus] Error de parsing: {ex}")
                if page.controls:
                    page.controls[0].disabled = False
                page.update()
            except ConnectionError as ex:
                print(f"[escuchar_bus] Conexión perdida: {ex}")
                break
            except Exception as ex:
                print(f"[escuchar_bus] Error inesperado: {ex}")
                if page.controls:
                    page.controls[0].disabled = False
                page.update()

    page.run_thread(escuchar_bus)
    cambiar_vista("login")


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8000, host="0.0.0.0")