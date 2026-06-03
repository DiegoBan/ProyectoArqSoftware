import flet as ft
import json
from soa_lib import send_message

def vista_productos(page: ft.Page, sock, cambiar_vista_func):
    
    # --- [Formulario] Campos de Creación ---
    txt_nombre = ft.TextField(label="Nombre del Producto", width=350)
    txt_detalle = ft.TextField(label="Detalle / Descripción", width=350, multiline=True, min_lines=2, max_lines=4)
    
    txt_precio = ft.TextField(
        label="Precio", 
        width=350, 
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string="")
    )

    productos_pendientes_list = []

    lista_pendientes_view = ft.Column(
        controls=[ft.Text("No hay productos pendientes de aprobación.", color=ft.Colors.GREY_500)],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    def actualizar_lista_pendientes():
        if not productos_pendientes_list:
            lista_pendientes_view.controls = [ft.Text("No hay productos pendientes de aprobación.", color=ft.Colors.GREY_500)]
        else:
            lista_pendientes_view.controls = [
                ft.ListTile(
                    leading=ft.Icon(name="hourglass_empty", color=ft.Colors.ORANGE_400),
                    title=ft.Text(p["nombre"], weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(f"Precio: ${p['precio']} | {p['detalle']}"),
                    trailing=ft.Chip(label=ft.Text("Pendiente"))
                ) for p in productos_pendientes_list
            ]
        page.update()

    # --- Lógica de Envío ---
    def btn_crear_producto_click(e):
        if not txt_nombre.value or not txt_precio.value or not txt_detalle.value:
            page.snack_bar = ft.SnackBar(ft.Text("Todos los campos son obligatorios"), bgcolor=ft.Colors.ORANGE_700)
            page.snack_bar.open = True
            page.update()
            return
        
        payload = {
            "accion": "crear_producto",
            "nombre": txt_nombre.value,
            "detalle": txt_detalle.value,
            "precio": int(txt_precio.value),
            "estado": "pendiente"
        }
        
        send_message(sock, "produ", json.dumps(payload))
        
        productos_pendientes_list.append(payload)
        actualizar_lista_pendientes()

        txt_nombre.value = ""
        txt_detalle.value = ""
        txt_precio.value = ""
        
        page.snack_bar = ft.SnackBar(ft.Text("Producto enviado a revisión"), bgcolor=ft.Colors.GREEN_700)
        page.snack_bar.open = True
        page.update()

    btn_guardar = ft.Button("Subir Producto", on_click=btn_crear_producto_click, width=350, height=45)
    btn_volver = ft.TextButton("Volver al Dashboard", on_click=lambda _: cambiar_vista_func("dashboard"))

    # --- Vistas de Contenido ---
    content_crear = ft.Column(
        controls=[
            ft.Text("Registrar Nuevo Producto", size=22, weight=ft.FontWeight.BOLD),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            txt_nombre,
            txt_detalle,
            txt_precio,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            btn_guardar,
            btn_volver
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    content_pendientes = ft.Column(
        controls=[
            ft.Text("Productos Esperando Aprobación", size=22, weight=ft.FontWeight.BOLD),
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            lista_pendientes_view
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        visible=False # Oculto por defecto
    )

    # --- Sistema de Navegación Alternativo (Ultra-Compatible) ---
    def cambiar_pestana(e):
        if e.control.text == "Crear Producto":
            content_crear.visible = True
            content_pendientes.visible = False
            btn_tab1.bgcolor = ft.Colors.BLUE_GREY_800
            btn_tab2.bgcolor = None
        else:
            content_crear.visible = False
            content_pendientes.visible = True
            btn_tab1.bgcolor = None
            btn_tab2.bgcolor = ft.Colors.BLUE_GREY_800
        page.update()

    btn_tab1 = ft.TextButton("Crear Producto", on_click=cambiar_pestana, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), bgcolor=ft.Colors.BLUE_GREY_800)
    btn_tab2 = ft.TextButton("Ver Pendientes", on_click=cambiar_pestana, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)))

    menu_superior = ft.Row(
        controls=[btn_tab1, btn_tab2],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )

    # --- Contenedor Principal ---
    contenedor_vistas = ft.Column(
        controls=[
            menu_superior,
            ft.Divider(height=20, color=ft.Colors.GREY_700),
            content_crear,
            content_pendientes
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    return ft.Container(
        content=contenedor_vistas,
        alignment=ft.Alignment.CENTER,
        expand=True,
        padding=20
    )