import flet as ft
import threading
import json
from soa_lib import connect_to_bus, send_message, receive_message

# Importamos las vistas
from vistas.crearuser import vista_crear_usuario
from vistas.login import vista_login
from vistas.home import vista_dashboard

def main(page: ft.Page):
    page.title = "Frontend SOA ERP"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

    # 1. Conexión al Bus
    try:
        sock = connect_to_bus()
        send_message(sock, "sinit", "clien")
        print("Frontend conectado al bus como 'clien'")
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
                        
                        page.snack_bar = ft.SnackBar(ft.Text("Acceso Concedido"), bgcolor=ft.Colors.GREEN_700)
                        page.snack_bar.open = True
                        cambiar_vista("dashboard")
                    
                    else:
                        # --- 2. ES OTRA OPERACIÓN (Ej: Crear Usuario) ---
                        mensaje_exito = respuesta.get("mensaje", "Operación realizada con éxito")
                        page.snack_bar = ft.SnackBar(ft.Text(mensaje_exito), bgcolor=ft.Colors.GREEN_700)
                        page.snack_bar.open = True
                        
                        # Desbloqueamos la pantalla para seguir trabajando
                        if len(page.controls) > 0:
                            page.controls[0].disabled = False
                
                else:
                    # --- 3. MANEJO DE ERRORES GENERAL EN PANTALLA ---
                    error_msg = respuesta.get("mensaje", "Error en la operación")
                    
                    # Extraemos detalles extra si el backend los manda (como en tu log)
                    if "detalles" in respuesta:
                        valores_detalles = list(respuesta.get("detalles").values())
                        if valores_detalles:
                            error_msg += f" ({valores_detalles[0]})"
                            
                    # Mostramos el error en la barra inferior
                    page.snack_bar = ft.SnackBar(ft.Text(error_msg), bgcolor=ft.Colors.RED_700)
                    page.snack_bar.open = True
                    
                    # Desbloqueamos la pantalla sin cambiar de vista
                    if len(page.controls) > 0:
                        page.controls[0].disabled = False 
                
                page.update()
                
            except Exception as ex:
                print(f"Error procesando mensaje entrante: {ex}")

    # Iniciar el hilo escuchador
    hilo = threading.Thread(target=escuchar_bus, daemon=True)
    hilo.start()

    # Arrancar la aplicación en la vista por defecto (Login)
    cambiar_vista("login")

if __name__ == "__main__":
    # Recuerda ejecutar en terminal: LIBGL_ALWAYS_SOFTWARE=1 python main.py
    ft.app(main)