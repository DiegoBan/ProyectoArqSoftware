import flet as ft
import json
from soa_lib import send_message
# Importamos el diccionario global desde la vista de productos
from vistas.productos import DATOS_PROD_TEMPORAL

def vista_confirmar_producto(page: ft.Page, sock, cambiar_vista_func):
    global DATOS_PROD_TEMPORAL
    
    # Leer los datos directamente desde Python puro
    nombre = DATOS_PROD_TEMPORAL["nombre"]
    detalle = DATOS_PROD_TEMPORAL["detalle"]
    precio = DATOS_PROD_TEMPORAL["precio"]

    def btn_confirmar_click(e):
        payload = {
            "accion": "crear_producto",
            "nombre": nombre,
            "detalle": detalle,
            "precio": int(precio),
            "estado": "pendiente"
        }
        
        # Despachar al bus
        send_message(sock, "produ", json.dumps(payload))
        
        # Limpiar el contenedor global para dejar el formulario vacío la próxima vez
        DATOS_PROD_TEMPORAL["nombre"] = ""
        DATOS_PROD_TEMPORAL["detalle"] = ""
        DATOS_PROD_TEMPORAL["precio"] = ""
        
        page.snack_bar = ft.SnackBar(ft.Text("Producto registrado con éxito"), bgcolor=ft.Colors.GREEN_700)
        page.snack_bar.open = True
        
        cambiar_vista_func("productos")

    btn_confirmar = ft.ElevatedButton("Confirmar y Guardar", on_click=btn_confirmar_click, width=350, height=45, bgcolor=ft.Colors.BLUE_700)
    btn_cancelar = ft.TextButton("Volver a Modificar", on_click=lambda _: cambiar_vista_func("productos"))

    resumen_tarjeta = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("¿Seguro que desea subir este producto?", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Text("Resumen de los datos del producto:", size=14, color=ft.Colors.GREY_400),
                ft.Divider(height=20, color=ft.Colors.GREY_700),
                ft.Text(f"Nombre: {nombre}", size=16, weight=ft.FontWeight.W_500),
                ft.Text(f"Precio: ${int(precio):,}", size=16, weight=ft.FontWeight.W_500),
                ft.Text(f"Detalle: {detalle}", size=14, color=ft.Colors.GREY_300),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                btn_confirmar,
                btn_cancelar
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True
        ),
        padding=30,
        bgcolor=ft.Colors.SURFACE_VARIANT,
        border_radius=10,
        width=400
    )

    return ft.Container(
        content=resumen_tarjeta,
        alignment=ft.Alignment.CENTER,
        expand=True
    )