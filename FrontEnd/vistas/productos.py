import flet as ft
import json
from soa_lib import send_message

def vista_productos(page: ft.Page, sock, cambiar_vista_func):
    
    # --- [Pestaña 1] Campos del Formulario de Creación ---
    txt_nombre = ft.TextField(label="Nombre del Producto", width=350)
    txt_detalle = ft.TextField(label="Detalle / Descripción", width=350, multiline=True, min_lines=2, max_lines=4)
    
    # Input numérico estricto
    txt_precio = ft.TextField(
        label="Precio", 
        width=350, 
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string="")
    )

    # Lista local simulada para mostrar en la pestaña de "Pendientes"
    # Nota: En una fase avanzada, esta lista se alimentaría del backend mediante el bus.
    productos_pendientes_list = []

    # Contenedor visual dinámico para la lista de pendientes
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
                    leading=ft.Icon(ft.icons.HOURGLASS_EMPTY, color=ft.Colors.ORANGE_400),
                    title=ft.Text(p["nombre"], weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(f"Precio: ${p['precio']} | {p['detalle']}"),
                    trailing=ft.Chip(label="Pendiente", bgcolor=ft.Colors.SURFACE_VARIANT)
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
        
        # Enviar al servicio de productos ("produ") a través del Bus
        send_message(sock, "produ", json.dumps(payload))
        
        # Añadir a la pestaña local de pendientes para feedback inmediato
        productos_pendientes_list.append(payload)
        actualizar_lista_pendientes()

        # Limpiar formulario
        txt_nombre.value = ""
        txt_detalle.value = ""
        txt_precio.value = ""
        
        page.snack_bar = ft.SnackBar(ft.Text("Producto enviado a revisión"), bgcolor=ft.Colors.GREEN_700)
        page.snack_bar.open = True
        page.update()

    btn_guardar = ft.Button("Subir Producto", on_click=btn_crear_producto_click, width=350, height=45)
    btn_volver = ft.TextButton("Volver al Dashboard", on_click=lambda _: cambiar_vista_func("dashboard"))

    # --- Contenido de las Pestañas ---
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
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # --- Configuración del Tab ---
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Crear Producto", icon=ft.icons.ADD_BOX, content=ft.Container(content=content_crear, padding=20)),
            ft.Tab(text="Pendientes", icon=ft.icons.PENDING_ACTIONS, content=ft.Container(content=content_pendientes, padding=20)),
        ],
        expand=1
    )

    return ft.Container(
        content=tabs,
        alignment=ft.Alignment.CENTER,
        expand=True,
        padding=10
    )