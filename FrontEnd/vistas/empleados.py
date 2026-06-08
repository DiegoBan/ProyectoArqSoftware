import flet as ft
import json
from soa_lib import send_message

def vista_empleados(page: ft.Page, sock, cambiar_vista_func):
    
    lbl_seleccionado = ft.Text("Seleccione un empleado para modificar su rol", size=14, color=ft.Colors.GREY_400)
    rut_seleccionado = ""
    
    dropdown_nuevo_rol = ft.Dropdown(
        label="Nuevo Rol",
        width=200,
        options=[
            ft.dropdown.Option("admin"),
            ft.dropdown.Option("vendedor"),
            ft.dropdown.Option("bodeguero"),
            ft.dropdown.Option("finanzas")
        ]
    )

    def btn_actualizar_rol_click(e):
        if not rut_seleccionado or not dropdown_nuevo_rol.value:
            page.snack_bar = ft.SnackBar(ft.Text("Seleccione un empleado y un rol"), bgcolor=ft.Colors.ORANGE_700)
            page.snack_bar.open = True
            page.update()
            return
            
        payload = {
            "accion": "actualizar_rol",
            "user_rut": page.session.store.get("rut"), # El admin que hace el cambio
            "rut_empleado": rut_seleccionado,
            "nuevo_rol": dropdown_nuevo_rol.value
        }
        send_message(sock, "usuar", json.dumps(payload))
        # Opcional: mostrar mensaje de éxito y limpiar

    btn_actualizar = ft.ElevatedButton("Asignar Nuevo Rol", on_click=btn_actualizar_rol_click, bgcolor=ft.Colors.BLUE_700)

    # --- Tabla Visualización ---
    def seleccionar_empleado(e):
        # Simulación de selección
        nonlocal rut_seleccionado
        rut_seleccionado = "12.345.678-9" # Esto lo sacarías de la fila clickeada
        lbl_seleccionado.value = f"Empleado seleccionado: Juan Pérez ({rut_seleccionado})"
        page.update()

    tabla_empleados = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("RUT")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Rol Actual")),
            ft.DataColumn(ft.Text("Acción")),
        ],
        rows=[
            # Datos de ejemplo
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("12.345.678-9")),
                ft.DataCell(ft.Text("Juan Pérez")),
                ft.DataCell(ft.Text("vendedor")),
                ft.DataCell(ft.TextButton("Seleccionar", on_click=seleccionar_empleado)),
            ])
        ]
    )

    btn_volver = ft.TextButton("Volver al Dashboard", on_click=lambda _: cambiar_vista_func("dashboard"))

    return ft.Container(
        content=ft.Column([
            ft.Text("Gestión de Empleados y Roles", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            tabla_empleados,
            ft.Divider(height=20, color=ft.Colors.GREY_700),
            lbl_seleccionado,
            ft.Row([dropdown_nuevo_rol, btn_actualizar], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            btn_volver
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=20,
        expand=True
    )