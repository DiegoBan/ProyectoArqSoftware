import flet as ft

def vista_dashboard_ventas(page: ft.Page, sock, cambiar_vista_func):
    
    # Redirecciones a las sub-vistas
    def ir_a_nueva(e):
        cambiar_vista_func("nueva_cotizacion")
        
    def ir_a_estados(e):
        cambiar_vista_func("estado_cotizaciones")

    # Tarjeta para crear
    card_nueva = ft.Container(
        content=ft.Column([
            ft.Icon(name="add_shopping_cart", size=40, color=ft.Colors.BLUE_400),
            ft.Text("Nueva Cotización", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("Generar un nuevo documento de venta", size=12, color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=20,
        bgcolor=ft.Colors.GREY_900,
        border_radius=10,
        width=200,
        height=180,
        on_click=ir_a_nueva
    )

    # Tarjeta para ver estados
    card_estados = ft.Container(
        content=ft.Column([
            ft.Icon(name="assignment", size=40, color=ft.Colors.ORANGE_400),
            ft.Text("Estado Cotizaciones", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("Seguimiento, OCO y Facturación", size=12, color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=20,
        bgcolor=ft.Colors.GREY_900,
        border_radius=10,
        width=200,
        height=180,
        on_click=ir_a_estados
    )

    btn_volver = ft.TextButton("Volver al Dashboard Principal", on_click=lambda _: cambiar_vista_func("dashboard"))

    return ft.Container(
        content=ft.Column([
            ft.Text("Módulo de Ventas", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Seleccione la acción que desea realizar", size=14, color=ft.Colors.GREY_400),
            ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
            ft.Row([card_nueva, card_estados], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
            btn_volver
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        alignment=ft.Alignment.CENTER,
        expand=True
    )