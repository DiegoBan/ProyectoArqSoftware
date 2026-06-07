import flet as ft

# 1. Diccionario sincronizado con las columnas de tu BD
DATOS_PROD_TEMPORAL = {
    "nombre": "",
    "familia": "",
    "subfamilia": "",
    "descripcion": "",
    "PN": "",
    "serie": ""
}
 
def vista_productos(page: ft.Page, sock, cambiar_vista_func):
    global DATOS_PROD_TEMPORAL
    
    # 2. Labels y propiedades corregidas para cada campo
    txt_nombre = ft.TextField(label="Nombre del Producto", width=350)
    txt_familia = ft.TextField(label="Familia", width=350)
    txt_subfamilia = ft.TextField(label="Subfamilia ", width=350)
    txt_descripcion = ft.TextField(label="Descripción", width=350, multiline=True, min_lines=2, max_lines=4)
    txt_PN = ft.TextField(label="Part Number / PN ", width=350)
    txt_serie = ft.TextField(label="Serie (Max 5 caract.)", width=350, max_length=5)

    # 3. Cargar datos temporales en los campos correctos
    if DATOS_PROD_TEMPORAL["nombre"]:
        txt_nombre.value = DATOS_PROD_TEMPORAL["nombre"]
        txt_familia.value = DATOS_PROD_TEMPORAL["familia"]
        txt_subfamilia.value = DATOS_PROD_TEMPORAL["subfamilia"]
        txt_descripcion.value = DATOS_PROD_TEMPORAL["descripcion"]
        txt_PN.value = DATOS_PROD_TEMPORAL["PN"]
        txt_serie.value = DATOS_PROD_TEMPORAL["serie"]
        
    def btn_crear_producto_click(e):
        # 4. Validar solo los campos NOT NULL de tu base de datos
        if not txt_nombre.value or not txt_familia.value or not txt_descripcion.value:
            page.snack_bar = ft.SnackBar(ft.Text("Nombre, Familia y Descripción son obligatorios"), bgcolor=ft.Colors.ORANGE_700)
            page.snack_bar.open = True
            page.update()
            return
        
        # 5. Guardar los valores usando las llaves actualizadas
        DATOS_PROD_TEMPORAL["nombre"] = txt_nombre.value
        DATOS_PROD_TEMPORAL["familia"] = txt_familia.value
        DATOS_PROD_TEMPORAL["subfamilia"] = txt_subfamilia.value
        DATOS_PROD_TEMPORAL["descripcion"] = txt_descripcion.value
        DATOS_PROD_TEMPORAL["PN"] = txt_PN.value
        DATOS_PROD_TEMPORAL["serie"] = txt_serie.value
        
        cambiar_vista_func("confirmar_producto")

    # ft.Button está obsoleto/alias en versiones nuevas de flet, mejor usar ElevatedButton
    btn_guardar = ft.ElevatedButton("Subir Producto", on_click=btn_crear_producto_click, width=350, height=45)
    btn_volver = ft.TextButton("Volver al Dashboard", on_click=lambda _: cambiar_vista_func("dashboard"))

    # 6. Estructura visual con todos los campos y Scroll habilitado
    content_crear = ft.Column(
        controls=[
            ft.Text("Registrar Nuevo Producto", size=26, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            txt_nombre,
            txt_familia,
            txt_subfamilia,
            txt_descripcion,
            txt_PN,
            txt_serie,
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            btn_guardar,
            btn_volver
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO
    )

    return ft.Container(
        content=content_crear,
        alignment=ft.Alignment.CENTER,
        expand=True,
        padding=20
    )