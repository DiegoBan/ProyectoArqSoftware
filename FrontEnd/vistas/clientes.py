import flet as ft
import json
from soa_lib import send_message

LISTA_CLIENTES = []

def vista_clientes(page: ft.Page, sock, cambiar_vista_func):
    global LISTA_CLIENTES
    es_admin = (page.session.store.get("rol") == "admin")

    # Estado de edición: si hay un cliente seleccionado, guardamos su rut original
    modo_edicion = {"rut_original": None}

    txt_rut = ft.TextField(label="RUT Empresa", width=300, disabled=not es_admin)
    txt_nombre = ft.TextField(label="Razón Social", width=300, disabled=not es_admin)
    lbl_modo = ft.Text("", color=ft.Colors.BLUE_300, size=12)

    def limpiar_formulario():
        txt_rut.value = ""
        txt_nombre.value = ""
        txt_rut.disabled = not es_admin
        lbl_modo.value = ""
        modo_edicion["rut_original"] = None
        page.update()

    def cargar_en_formulario(rut, nombre):
        modo_edicion["rut_original"] = str(rut)
        txt_rut.value = str(rut) if rut else ""
        txt_rut.disabled = True  # No permitir cambiar el RUT al editar
        txt_nombre.value = str(nombre) if nombre else ""
        lbl_modo.value = f"Editando cliente: {rut}"
        page.update()

    def btn_guardar_click(e):
        if not txt_rut.value or not txt_nombre.value:
            page.overlay.append(ft.SnackBar(ft.Text("Complete todos los campos"), bgcolor=ft.Colors.ORANGE_700))
            page.overlay[-1].open = True
            page.update()
            return

        # Decidir acción según si estamos editando o creando
        if modo_edicion["rut_original"] is not None:
            accion = "actualizar_cliente"
            payload = {
                "accion": accion,
                "user_rut": page.session.store.get("rut"),
                "rut_empresa": modo_edicion["rut_original"],
                "nombre": txt_nombre.value
            }
        else:
            accion = "crear_cliente"
            payload = {
                "accion": accion,
                "user_rut": page.session.store.get("rut"),
                "rut_empresa": txt_rut.value,
                "nombre": txt_nombre.value
            }

        send_message(sock, "clien", json.dumps(payload))
        if page.controls:
            page.controls[0].disabled = True
        page.update()

    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("RUT")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Acción")),
        ],
        rows=[]
    )

    for cli in LISTA_CLIENTES:
        tabla.rows.append(ft.DataRow(cells=[
            ft.DataCell(ft.Text(str(cli.get("id", "")))),
            ft.DataCell(ft.Text(str(cli.get("rut_empresa", "")))),
            ft.DataCell(ft.Text(str(cli.get("nombre", "")))),
            ft.DataCell(
                ft.TextButton(
                    "Editar",
                    on_click=lambda e, r=cli.get("rut_empresa"), n=cli.get("nombre"): cargar_en_formulario(r, n)
                )
            )
        ]))

    if not LISTA_CLIENTES:
        send_message(sock, "clien", json.dumps({
            "accion": "obtener_clientes",
            "user_rut": page.session.store.get("rut")
        }))

    return ft.Container(
        content=ft.Column([
            ft.Text("Gestión de Clientes", size=24, weight="bold"),
            ft.Row([
                ft.Column([
                    lbl_modo,
                    txt_rut,
                    txt_nombre,
                    ft.Row([
                        ft.ElevatedButton("Guardar", on_click=btn_guardar_click, visible=es_admin),
                        ft.TextButton("Limpiar", on_click=lambda _: limpiar_formulario(), visible=es_admin),
                    ])
                ]),
                tabla
            ]),
            ft.TextButton("← Volver al Dashboard", on_click=lambda _: cambiar_vista_func("dashboard"))
        ]),
        padding=20
    )