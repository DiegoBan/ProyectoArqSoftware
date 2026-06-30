import flet as ft
import json
from soa_lib import send_message

LISTA_EMPLEADOS = []

# FIX preventivo: igual que en historial_ventas.py, usar "if not LISTA_EMPLEADOS"
# para decidir si pedir datos sería un bug si alguna vez la respuesta real es
# una lista vacía (ej. tabla de usuarios vacía por algún motivo). [] es falsy
# en Python, así que se entraría en un bucle de pedidos infinitos. Se usa un
# flag explícito para evitarlo, aunque en este caso siempre exista al menos
# un admin.
YA_CARGADO = False

def vista_empleados(page: ft.Page, sock, cambiar_vista_func):
    global LISTA_EMPLEADOS

    # FIX: usar lista mutable en lugar de string simple para que el closure lo capture bien
    estado = {"rut_seleccionado": ""}

    lbl_sel = ft.Text("Seleccione un empleado de la tabla", color=ft.Colors.GREY_400)
    dropdown = ft.Dropdown(
        label="Nuevo Rol",
        width=200,
        options=[ft.dropdown.Option(r) for r in ["admin", "vendedor", "bodeguero", "finanzas"]]
    )

    def btn_actualizar_click(e):
        if not estado["rut_seleccionado"]:
            page.overlay.append(ft.SnackBar(ft.Text("Seleccione un empleado primero"), bgcolor=ft.Colors.ORANGE_700))
            page.overlay[-1].open = True
            page.update()
            return
        if not dropdown.value:
            page.overlay.append(ft.SnackBar(ft.Text("Seleccione un rol"), bgcolor=ft.Colors.ORANGE_700))
            page.overlay[-1].open = True
            page.update()
            return

        send_message(sock, "usuar", json.dumps({
            "accion": "actualizar_rol",
            "user_rut": page.session.store.get("rut"),
            "rut_empleado": estado["rut_seleccionado"],
            "nuevo_rol": dropdown.value
        }))
        # Deshabilitar la vista entera mientras espera respuesta del bus
        if page.controls:
            page.controls[0].disabled = True
        page.update()

    def seleccionar_empleado(rut, nombre):
        # FIX: modificar el dict mutable, no una variable local
        estado["rut_seleccionado"] = rut
        lbl_sel.value = f"Empleado seleccionado: {nombre} ({rut})"
        lbl_sel.color = ft.Colors.BLUE_300
        page.update()

    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("RUT")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Rol")),
            ft.DataColumn(ft.Text("Acción")),
        ],
        rows=[]
    )

    for emp in LISTA_EMPLEADOS:
        tabla.rows.append(ft.DataRow(cells=[
            ft.DataCell(ft.Text(emp.get("rut", ""))),
            ft.DataCell(ft.Text(emp.get("nombre", ""))),
            ft.DataCell(ft.Text(emp.get("rol", ""))),
            ft.DataCell(
                ft.TextButton(
                    "Seleccionar",
                    # FIX: capturar valores en parámetros por defecto del lambda
                    on_click=lambda e, r=emp.get("rut"), n=emp.get("nombre"): seleccionar_empleado(r, n)
                )
            )
        ]))

    global YA_CARGADO
    if not YA_CARGADO:
        YA_CARGADO = True
        send_message(sock, "usuar", json.dumps({
            "accion": "obtener_usuarios",
            "user_rut": page.session.store.get("rut")
        }))

    return ft.Container(
        content=ft.Column([
            ft.Text("Gestión de Empleados", size=24, weight="bold"),
            tabla,
            ft.Divider(),
            lbl_sel,
            ft.Row([dropdown, ft.ElevatedButton("Asignar Rol", on_click=btn_actualizar_click)]),
            ft.TextButton("← Volver al Dashboard", on_click=lambda _: cambiar_vista_func("dashboard"))
        ]),
        padding=20
    )