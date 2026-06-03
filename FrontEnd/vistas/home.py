import flet as ft

def vista_dashboard(page: ft.Page, sock, cambiar_vista_func):
    
    # 1. Rescatamos los datos de la memoria temporal (sesión)
    rol_usuario = page.session.store.get("rol")
    nombre_usuario = page.session.store.get("nombre")

    # 2. Construimos la base del menú
    controles_menu = [
        ft.Text(f"Bienvenido, {nombre_usuario}", size=32, weight=ft.FontWeight.BOLD),
        ft.Text(f"Nivel de acceso actual: {rol_usuario}", size=16, color=ft.Colors.BLUE_400),
        ft.Divider(height=30, color=ft.Colors.TRANSPARENT)
    ]

    # 3. FILTRO DE SEGURIDAD (RBAC)
    if rol_usuario == "admin":
        # Este botón SOLO se agrega a la pantalla si el rol es exactamente 'admin'
        btn_crear_user = ft.Button(
            "Administración: Crear Nuevo Usuario", 
            icon="person_add",
            on_click=lambda _: cambiar_vista_func("crear_usuario"),
            width=350, height=45
        )
        controles_menu.append(btn_crear_user)
        controles_menu.append(ft.Divider(height=10, color=ft.Colors.TRANSPARENT))
        
        # --- NUEVO Botón: Gestión de Productos ---
        btn_productos = ft.Button(
            "Administración: Gestión de Productos", 
            icon="shopping_bag", # Icono de bolsa/producto
            on_click=lambda _: cambiar_vista_func("productos"), # Redirige a la vista de productos
            width=350, height=45
        )
        controles_menu.append(btn_productos)
        controles_menu.append(ft.Divider(height=10, color=ft.Colors.TRANSPARENT))

        # --- NUEVO Botón: Módulo de Ventas / Cotizaciones ---
        btn_ventas = ft.Button(
            "Administración: Ventas y Cotizaciones", 
            icon="point_of_sale", # Icono de caja registradora / ventas
            on_click=lambda _: cambiar_vista_func("ventas"), # Redirige a la vista de ventas
            width=350, height=45
        )
        controles_menu.append(btn_ventas)
        controles_menu.append(ft.Divider(height=10, color=ft.Colors.TRANSPARENT))
    # (Aquí a futuro agregaremos los botones de Inventario, Ventas, etc. según el rol)

    # 4. Botón de Cerrar Sesión (Visible para todos)
    def btn_cerrar_sesion_click(e):
        page.session.store.clear() # Borramos los datos de seguridad por precaución
        cambiar_vista_func("login")

    btn_salir = ft.TextButton("Cerrar Sesión", on_click=btn_cerrar_sesion_click)
    controles_menu.append(btn_salir)

    return ft.Container(
        content=ft.Column(controles_menu, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER), 
        alignment=ft.Alignment(0, 0), 
        expand=True,
        padding=20
    )