import flet as ft
import json
from soa_lib import connect_to_bus, send_message, receive_message

# Importar las vistas
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
        print("Frontend conectado al bus como 'front'")
    except Exception as e:
        page.add(ft.Text(f"Error crítico conectando al bus: {e}", color=ft.Colors.RED))
        return

    # 2. Función de Enrutamiento (Navegación)
    def cambiar_vista(nombre_vista):
        page.controls.clear()

        if nombre_vista == "login":
            page.add(vista_login(page, sock)) 
        elif nombre_vista == "crear_usuario":
            page.add(vista_crear_usuario(page, sock, cambiar_vista))
        elif nombre_vista == "dashboard":
            page.add(vista_dashboard(page, sock, cambiar_vista))
        elif nombre_vista == "productos":
            page.add(vista_productos(page, sock, cambiar_vista))
        elif nombre_vista == "confirmar_producto":
            page.add(vista_confirmar_producto(page, sock, cambiar_vista))
        elif nombre_vista == "ventas":
            page.add(vista_dashboard_ventas(page, sock, cambiar_vista))
        elif nombre_vista == "nueva_cotizacion":
            page.add(vista_nueva_cotizacion(page, sock, cambiar_vista))
        elif nombre_vista == "estado_cotizaciones":
            page.add(vista_estado_cotizaciones(page, sock, cambiar_vista))
        elif nombre_vista == "clientes":
            page.add(vista_clientes(page, sock, cambiar_vista))
        elif nombre_vista == "empleados":
            page.add(vista_empleados(page, sock, cambiar_vista))

        page.update()

    # 3. Hilo de Escucha 
    def escuchar_bus():
        while True:
            try:
                data = receive_message(sock)
                if not data:
                    print("El bus cerró la conexión.")
                    break
                
                # Descartar los 5 caracteres de la cabecera ("clien")
                mensaje_crudo = data[5:].decode()
                
                try:
                    respuesta = json.loads(mensaje_crudo)
                except json.JSONDecodeError:
                    # Ignoramos mensajes puros del bus que no son JSON
                    continue 
                
                if respuesta.get("estado") == "ok":
                    if "usuario" in respuesta:
                        # --- 1. ES UNA RESPUESTA DE INICIO DE SESIÓN ---
                        usuario = respuesta.get("usuario", {})
                        page.session.store.set("rol", str(usuario.get("rol"))) 
                        page.session.store.set("nombre", usuario.get("nombre"))
                        page.session.store.set("rut", usuario.get("rut"))
                        
                        alerta_exito = ft.SnackBar(ft.Text("Acceso Concedido"), bgcolor=ft.Colors.GREEN_700)
                        page.overlay.append(alerta_exito)
                        alerta_exito.open = True
                        
                        cambiar_vista("dashboard")
                    
                    else:
                        # --- 2. ES OTRA OPERACIÓN (Ej: Crear Usuario) ---
                        mensaje_exito = respuesta.get("mensaje", "Operación realizada con éxito")
                        
                        alerta_exito_op = ft.SnackBar(ft.Text(mensaje_exito), bgcolor=ft.Colors.GREEN_700)
                        page.overlay.append(alerta_exito_op)
                        alerta_exito_op.open = True
                        
                        # Desbloqueamos la pantalla para seguir trabajando
                        if len(page.controls) > 0:
                            page.controls[0].disabled = False
                
                else:
                    # --- 3. MANEJO DE ERRORES GENERAL EN PANTALLA ---
                    error_msg = respuesta.get("mensaje", "Error en la operación")
                    
                    # Extraemos detalles extra si el backend los manda
                    if "detalles" in respuesta:
                        valores_detalles = list(respuesta.get("detalles").values())
                        if valores_detalles:
                            error_msg += f" ({valores_detalles[0]})"
                            
                    # NUEVA forma de mostrar el error rojo
                    alerta_error = ft.SnackBar(ft.Text(error_msg), bgcolor=ft.Colors.RED_700)
                    page.overlay.append(alerta_error)
                    alerta_error.open = True
                    
                    # Desbloqueamos la pantalla para que el usuario pueda intentar de nuevo
                    if len(page.controls) > 0:
                        page.controls[0].disabled = False 
                
                page.update()
                
            except Exception as ex:
                # 1. Mostrar en la terminal
                print(f"Error procesando mensaje entrante: {ex}")
                
                # 2. Mostrar en la pantalla del usuario 
                page.snack_bar = ft.SnackBar(ft.Text(f"Error crítico en el cliente: {ex}"), bgcolor=ft.Colors.RED_900)
                page.snack_bar.open = True
                
                # 3. Desbloquear la pantalla por si se había quedado "pensando"
                if len(page.controls) > 0:
                    page.controls[0].disabled = False
                page.update()
                

    # Iniciar el hilo escuchador
    page.run_thread(escuchar_bus)

    # Arrancar la aplicación en la vista por defecto (Login)
    cambiar_vista("login")

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8000, host="0.0.0.0")