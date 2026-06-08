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
        respuesta_init = receive_message(sock) 
        print(f"El bus nos recibió con: {respuesta_init}")

        print("Frontend conectado al bus como 'front'")
    except Exception as e:
        page.add(ft.Text(f"Error crítico conectando al bus: {e}", color=ft.Colors.RED))
        return

    # 2. Función de Enrutamiento (Navegación)
    def cambiar_vista(nombre_vista):
        page.controls.clear()

        if nombre_vista == "login":
            page.add(vista_login(page, sock, cambiar_vista)) 
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
    # Arrancar la aplicación en la vista por defecto (Login)
    cambiar_vista("login")

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8000, host="0.0.0.0")