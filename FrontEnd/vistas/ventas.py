import flet as ft

def vista_dashboard_ventas(page: ft.Page, sock, cambiar_vista_func):
    
    def ir_a_nueva(e):
        cambiar_vista_func("nueva_cotizacion")
        
    def ir_a_estados(e):
        cambiar_vista_func("estado_cotizaciones")

    # Usamos EXACTAMENTE la misma sintaxis que te funciona en tu home.py:
    # ft.Button("Texto", icon="nombre_icono", width=..., height=...)
    btn_nueva_cotizacion = ft.Button(
        "Nueva Cotización", 
        icon="add_shopping_cart",
        on_click=ir_a_nueva,
        width=350, 
        height=45
    )

    btn_estado_cotizaciones = ft.Button(
        "Estado Cotizaciones", 
        icon="assignment",
        on_click=ir_a_estados,
        width=350, 
        height=45
    )

    btn_volver = ft.TextButton(
        "Volver al Dashboard Principal", 
        on_click=lambda _: cambiar_vista_func("dashboard")
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Módulo de Ventas", size=26, weight=ft.FontWeight.BOLD),
                ft.Text("Seleccione la acción que desea realizar", size=14, color=ft.Colors.GREY_400),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                btn_nueva_cotizacion,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                btn_estado_cotizaciones,
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                btn_volver
            ], 
            alignment=ft.MainAxisAlignment.CENTER, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        alignment=ft.Alignment(0, 0),
        expand=True,
        padding=20
    )