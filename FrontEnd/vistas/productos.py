import flet as ft
import json
from soa_lib import send_message

def vista_productos(page: ft.Page, sock, cambiar_vista_func):
    
    # --- Campos de Formulario ---
    txt_nombre = ft.TextField(label="Nombre del Producto", width=350)
    txt_detalle = ft.TextField(label="Detalle / Descripción", width=350, multiline=True, min_lines=2, max_lines=4)
    
    txt_precio = ft.TextField(
        label="Precio", 
        width=350, 
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string="")
    )

    # --- Diálogo de Confirmación (Pop-up) ---
    def cerrar_modal(e):
        dialogo_confirmacion.open = False
        page.update()

    def confirmar_y_enviar(e):
        # 1. Armar el payload definitivo
        payload = {
            "accion": "crear_producto",
            "nombre": txt_nombre.value,
            "detalle": txt_detalle.value,
            "precio": int(txt_precio.value),
            "estado": "pendiente"
        }
        
        # 2. Despachar al bus de servicios
        send_message(sock, "produ", json.dumps(payload))
        
        # 3. Cerrar el modal limpiamente
        dialogo_confirmacion.open = False
        
        # 4. Limpiar los campos del formulario principal
        txt_nombre.value = ""
        txt_detalle.value = ""
        txt_precio.value = ""
        
        page.update()

    # Estructura del Pop-up intermedio
    dialogo_confirmacion = ft.AlertDialog(
        modal=True, # Bloquea el click fuera del recuadro
        title=ft.Text("¿Seguro que desea subir este producto?", size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        content=ft.Column(
            controls=[
                ft.Text("Resumen de los datos ingresados:", size=14, color=ft.Colors.GREY_400),
                ft.Divider(height=10, color=ft.Colors.GREY_700),
                # Estos textos se rellenan dinámicamente al presionar el botón principal
                lbl_resumen_nombre := ft.Text("", weight=ft.FontWeight.W_500),
                lbl_resumen_precio := ft.Text("", weight=ft.FontWeight.W_500),
                lbl_resumen_detalle := ft.Text("", size=13, color=ft.Colors.GREY_300),
            ],
            tight=True,
            width=320
        ),
        actions=[
            ft.TextButton("Volver", on_click=cerrar_modal),
            ft.ElevatedButton("Confirmar", on_click=confirmar_y_enviar, bgcolor=ft.Colors.BLUE_700)
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    # --- Lógica del Botón Principal ---
    def btn_crear_producto_click(e):
        # Validar campos vacíos primero
        if not txt_nombre.value or not txt_precio.value or not txt_detalle.value:
            page.snack_bar = ft.SnackBar(ft.Text("Todos los campos son obligatorios"), bgcolor=ft.Colors.ORANGE_700)
            page.snack_bar.open = True
            page.update()
            return
        
        # Inyectar los datos del formulario al contenido del pop-up
        lbl_resumen_nombre.value = f"Nombre: {txt_nombre.value}"
        lbl_resumen_precio.value = f"Precio: ${int(txt_precio.value):,}" # Formato de miles básico
        lbl_resumen_detalle.value = f"Detalle: {txt_detalle.value}"
        
        # Levantar el modal sobre la interfaz actual
        page.dialog = dialogo_confirmacion
        dialogo_confirmacion.open = True
        page.update()

    btn_guardar = ft.Button("Subir Producto", on_click=btn_crear_producto_click, width=350, height=45)
    btn_volver = ft.TextButton("Volver al Dashboard", on_click=lambda _: cambiar_vista_func("dashboard"))

    # --- Estructura Visual Unificada ---
    content_crear = ft.Column(
        controls=[
            ft.Text("Registrar Nuevo Producto", size=26, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            txt_nombre,
            txt_detalle,
            txt_precio,
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            btn_guardar,
            btn_volver
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    return ft.Container(
        content=content_crear,
        alignment=ft.Alignment.CENTER,
        expand=True,
        padding=20
    )