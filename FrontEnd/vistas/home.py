import flet as ft

def vista_dashboard(page: ft.Page, sock, cambiar_vista_func):
    
    # 1. Rescatamos los datos de la memoria temporal (sesión)
    rol_usuario = page.session.get("rol")
    nombre_usuario = page.session.get("nombre")

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
            icon=ft.icons.PERSON_ADD,
            on_click=lambda _: cambiar_vista_func("crear_usuario"),
            width=350, height=45
        )
        controles_menu.append(btn_crear_user)
        controles_menu.append(ft.Divider(height=10, color=ft.Colors.TRANSPARENT))

    # (Aquí a futuro agregaremos los botones de Inventario, Ventas, etc. según el rol)

    # 4. Botón de Cerrar Sesión (Visible para todos)
    def btn_cerrar_sesion_click(e):
        page.session.clear() # Borramos los datos de seguridad por precaución
        cambiar_vista_func("login")

    btn_salir = ft.TextButton("Cerrar Sesión", on_click=btn_cerrar_sesion_click)
    controles_menu.append(btn_salir)

    return ft.Container(
        content=ft.Column(controles_menu, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER), 
        alignment=ft.Alignment(0, 0), 
        expand=True,
        padding=20
    )