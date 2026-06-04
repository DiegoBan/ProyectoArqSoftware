import flet as ft

# Variables globales para transferir los datos entre vistas sin usar la sesión de Flet
DATOS_PROD_TEMPORAL = {
    "nombre": "",
    "detalle": "",
    "precio": ""
}

def vista_productos(page: ft.Page, sock, cambiar_vista_func):
    global DATOS_PROD_TEMPORAL
    
    # --- Campos de Formulario ---
    txt_nombre = ft.TextField(label="Nombre del Producto", width=350)
    txt_detalle = ft.TextField(label="Detalle / Descripción", width=350, multiline=True, min_lines=2, max_lines=4)
    
    txt_precio = ft.TextField(
        label="Precio", 
        width=350, 
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string="")
    )

    # Si volvemos de la vista de confirmación, rellenar con lo que ya se había escrito
    if DATOS_PROD_TEMPORAL["nombre"]:
        txt_nombre.value = DATOS_PROD_TEMPORAL["nombre"]
        txt_detalle.value = DATOS_PROD_TEMPORAL["detalle"]
        txt_precio.value = DATOS_PROD_TEMPORAL["precio"]

    # --- Lógica de Navegación ---
    def btn_crear_producto_click(e):
        if not txt_nombre.value or not txt_precio.value or not txt_detalle.value:
            page.snack_bar = ft.SnackBar(ft.Text("Todos los campos son obligatorios"), bgcolor=ft.Colors.ORANGE_700)
            page.snack_bar.open = True
            page.update()
            return
        
        # Guardar en el diccionario global nativo de Python
        DATOS_PROD_TEMPORAL["nombre"] = txt_nombre.value
        DATOS_PROD_TEMPORAL["detalle"] = txt_detalle.value
        DATOS_PROD_TEMPORAL["precio"] = txt_precio.value
        
        cambiar_vista_func("confirmar_producto")

    btn_guardar = ft.Button("Subir Producto", on_click=btn_crear_producto_click, width=350, height=45)
    btn_volver = ft.TextButton("Volver al Dashboard", on_click=lambda _: cambiar_vista_func("dashboard"))

    # --- Estructura Visual ---
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