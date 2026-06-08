import flet as ft
import json
from soa_lib import send_message

def vista_clientes(page: ft.Page, sock, cambiar_vista_func):
    rol_usuario = page.session.store.get("rol")
    es_admin = (rol_usuario == "admin")

    # --- 1. Formulario de Registro / Actualización ---
    txt_rut_empresa = ft.TextField(label="RUT Empresa", width=300, disabled=not es_admin)
    txt_nombre = ft.TextField(label="Razón Social / Nombre", width=300, disabled=not es_admin)
    
    def btn_guardar_cliente_click(e):
        if not txt_rut_empresa.value or not txt_nombre.value:
            page.snack_bar = ft.SnackBar(ft.Text("Complete los campos"), bgcolor=ft.Colors.ORANGE_700)
            page.snack_bar.open = True
            page.update()
            return
            
        payload = {
            "accion": "crear_cliente", # O 'actualizar_cliente' si decides separarlo
            "user_rut": page.session.store.get("rut"),
            "rut_empresa": txt_rut_empresa.value,
            "nombre": txt_nombre.value
        }
        send_message(sock, "clien", json.dumps(payload))
        txt_rut_empresa.value = ""
        txt_nombre.value = ""
        page.update()

    btn_guardar = ft.ElevatedButton("Guardar Cliente", on_click=btn_guardar_cliente_click, visible=es_admin, bgcolor=ft.Colors.BLUE_700)

    formulario_registro = ft.Column([
        ft.Text("Gestión de Clientes", size=20, weight=ft.FontWeight.BOLD),
        ft.Text("Ingrese datos para crear o modificar un cliente." if es_admin else "Modo de solo lectura. Contacte a un administrador para modificar.", size=12, color=ft.Colors.GREY_400),
        txt_rut_empresa,
        txt_nombre,
        btn_guardar
    ], alignment=ft.MainAxisAlignment.START)

    # --- 2. Visualización (Tabla) ---
    tabla_clientes = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("RUT Empresa")),
            ft.DataColumn(ft.Text("Razón Social")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[
            # Datos de ejemplo (A futuro esto se llenará con un request al backend)
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("1")),
                ft.DataCell(ft.Text("76.123.456-7")),
                ft.DataCell(ft.Text("Inversiones Alfa S.A.")),
                ft.DataCell(ft.TextButton("Editar", disabled=not es_admin)), # Botón bloqueado si no es admin
            ])
        ]
    )

    btn_volver = ft.TextButton("Volver al Dashboard", on_click=lambda _: cambiar_vista_func("dashboard"))

    # --- 3. Estructura Final ---
    return ft.Container(
        content=ft.Column([
            ft.Row([formulario_registro, tabla_clientes], alignment=ft.MainAxisAlignment.SPACE_EVENLY, vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            btn_volver
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=20,
        expand=True
    )