import flet as ft
import json
from soa_lib import send_message
from vistas.productos import DATOS_PROD_TEMPORAL

def vista_confirmar_producto(page: ft.Page, sock, cambiar_vista_func):
    global DATOS_PROD_TEMPORAL
    
    # 1. Obtener los datos reales del diccionario temporal
    nombre = DATOS_PROD_TEMPORAL["nombre"]
    familia = DATOS_PROD_TEMPORAL["familia"]
    subfamilia = DATOS_PROD_TEMPORAL["subfamilia"]
    descripcion = DATOS_PROD_TEMPORAL["descripcion"]
    PN = DATOS_PROD_TEMPORAL["PN"]
    serie = DATOS_PROD_TEMPORAL["serie"]

    def btn_confirmar_click(e):
        # En Flet 0.21.0+, se suele usar page.session.get()
        rut_admin_actual = page.session.store.get("rut") 

        # 2. Armar el payload EXACTAMENTE como lo espera tu microservicio
        payload = {
            "accion": "crear_producto",
            "user": rut_admin_actual, 
            "nombre": nombre,
            "familia": familia,
            "subfamilia": subfamilia,
            "descripcion": descripcion,
            "PN": PN,
            "serie": serie
        }
        
        send_message(sock, "produ", json.dumps(payload))
        
        # 3. Limpiar todas las llaves del diccionario temporal
        DATOS_PROD_TEMPORAL["nombre"] = ""
        DATOS_PROD_TEMPORAL["familia"] = ""
        DATOS_PROD_TEMPORAL["subfamilia"] = ""
        DATOS_PROD_TEMPORAL["descripcion"] = ""
        DATOS_PROD_TEMPORAL["PN"] = ""
        DATOS_PROD_TEMPORAL["serie"] = ""
        
        page.snack_bar = ft.SnackBar(ft.Text("Producto registrado con éxito"), bgcolor=ft.Colors.GREEN_700)
        page.snack_bar.open = True
        
        cambiar_vista_func("productos")

    btn_confirmar = ft.ElevatedButton("Confirmar y Guardar", on_click=btn_confirmar_click, width=350, height=45, bgcolor=ft.Colors.BLUE_700)
    btn_cancelar = ft.TextButton("Volver a Modificar", on_click=lambda _: cambiar_vista_func("productos"))

    # 4. Actualizar la tarjeta para mostrar los nuevos campos de la BD
    resumen_tarjeta = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("¿Seguro que desea subir este producto?", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Text("Resumen de los datos del producto:", size=14, color=ft.Colors.GREY_400),
                ft.Divider(height=20, color=ft.Colors.GREY_700),
                
                ft.Text(f"Nombre: {nombre}", size=16, weight=ft.FontWeight.W_500),
                ft.Text(f"Familia: {familia}", size=16, weight=ft.FontWeight.W_500),
                ft.Text(f"Subfamilia: {subfamilia if subfamilia else 'N/A'}", size=14, color=ft.Colors.GREY_300),
                ft.Text(f"Descripción: {descripcion}", size=14, color=ft.Colors.GREY_300),
                ft.Text(f"PN: {PN if PN else 'N/A'}", size=14, color=ft.Colors.GREY_300),
                ft.Text(f"Serie: {serie if serie else 'N/A'}", size=14, color=ft.Colors.GREY_300),
                
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                btn_confirmar,
                btn_cancelar
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True
        ),
        padding=30,
        bgcolor=ft.Colors.GREY_900,
        border_radius=10,
        width=400
    )

    return ft.Container(
        content=resumen_tarjeta,
        alignment=ft.Alignment.CENTER,
        expand=True
    )