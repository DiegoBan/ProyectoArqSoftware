import flet as ft
import json
from soa_lib import send_message
from vistas.crearuser import _rut_valido, _formatear_rut

LISTA_CLIENTES = []

# FIX preventivo: mismo riesgo de bucle infinito visto en historial_ventas.py
# si "if not LISTA_CLIENTES" coincide con una respuesta legítima de 0 clientes.
YA_CARGADO = False

def vista_clientes(page: ft.Page, sock, cambiar_vista_func):
    global LISTA_CLIENTES
    es_admin = (page.session.store.get("rol") == "admin")

    # Estado de edición: si hay un cliente seleccionado, guardamos su rut original
    modo_edicion = {"rut_original": None}

    txt_rut = ft.TextField(
        label="RUT Empresa (ej: 12.345.678-9)",
        width=300,
        disabled=not es_admin,
        max_length=12,
        hint_text="12.345.678-9",
        input_filter=ft.InputFilter(allow=True, regex_string=r"[\d\.\-kK]"),
    )
    txt_nombre = ft.TextField(label="Razón Social", width=300, disabled=not es_admin)

    def validar_rut_empresa(e):
        if txt_rut.disabled:
            return
        raw = txt_rut.value or ""
        formateado = _formatear_rut(raw)
        if formateado != raw:
            txt_rut.value = formateado
        valor = txt_rut.value.strip()
        if valor == "" or len(valor.replace(".", "").replace("-", "")) < 2:
            txt_rut.error_text = None
            txt_rut.suffix_icon = None
        elif _rut_valido(valor):
            txt_rut.error_text = None
            txt_rut.suffix_icon = ft.Icons.CHECK_CIRCLE
            txt_rut.suffix_style = ft.TextStyle(color=ft.Colors.GREEN_400)
        else:
            txt_rut.error_text = "RUT inválido"
            txt_rut.suffix_icon = ft.Icons.ERROR
        page.update()

    txt_rut.on_change = validar_rut_empresa
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

        # Validar RUT solo al crear (en edición el campo está deshabilitado)
        if modo_edicion["rut_original"] is None and not _rut_valido(txt_rut.value):
            page.overlay.append(ft.SnackBar(ft.Text("El RUT ingresado no es válido"), bgcolor=ft.Colors.RED_700))
            page.overlay[-1].open = True
            page.update()
            return

        rut_limpio = txt_rut.value.replace(".", "").replace("-", "").upper().replace("K", "0")
        rut_limpio = int(rut_limpio) if rut_limpio else 0

        # Decidir acción según si estamos editando o creando
        if modo_edicion["rut_original"] is not None:
            accion = "actualizar_cliente"
            payload = {
                "accion": accion,
                "user_rut": page.session.store.get("rut"),
                "rut_empresa": int(modo_edicion["rut_original"].replace(".", "").replace("-", "").upper().replace("K", "0")),
                "nombre": txt_nombre.value
            }
        else:
            accion = "crear_cliente"
            payload = {
                "accion": accion,
                "user_rut": page.session.store.get("rut"),
                "rut_empresa": rut_limpio,
                "nombre": txt_nombre.value
            }

        send_message(sock, "clien", json.dumps(payload))
        if page.controls:
            page.controls[0].disabled = True
        page.update()

    def btn_eliminar_click(rut_empresa):
        payload = {
            "accion": "eliminar_cliente",
            "user_rut": page.session.store.get("rut"),
            "rut_empresa": rut_empresa
        }
        send_message(sock, "clien", json.dumps(payload))
        if page.controls:
            page.controls[0].disabled = True
        page.update()

    def confirmar_eliminar(rut_empresa, nombre):
        # Diálogo de confirmación para evitar borrados accidentales
        def cerrar_dialogo(e):
            dialogo.open = False
            page.update()

        def ejecutar_eliminar(e):
            dialogo.open = False
            page.update()
            btn_eliminar_click(rut_empresa)

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Eliminar al cliente '{nombre}' (RUT {rut_empresa})? Esta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.TextButton("Eliminar", on_click=ejecutar_eliminar, style=ft.ButtonStyle(color=ft.Colors.RED_400)),
            ],
        )
        page.overlay.append(dialogo)
        dialogo.open = True
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
        acciones = [
            ft.TextButton(
                "Editar",
                on_click=lambda e, r=cli.get("rut_empresa"), n=cli.get("nombre"): cargar_en_formulario(r, n)
            )
        ]
        if es_admin:
            # NUEVO: opción de eliminar, solo visible para admins
            acciones.append(
                ft.TextButton(
                    "Eliminar",
                    style=ft.ButtonStyle(color=ft.Colors.RED_400),
                    on_click=lambda e, r=cli.get("rut_empresa"), n=cli.get("nombre"): confirmar_eliminar(r, n)
                )
            )
        tabla.rows.append(ft.DataRow(cells=[
            ft.DataCell(ft.Text(str(cli.get("id", "")))),
            ft.DataCell(ft.Text(str(cli.get("rut_empresa", "")))),
            ft.DataCell(ft.Text(str(cli.get("nombre", "")))),
            ft.DataCell(ft.Row(acciones))
        ]))

    global YA_CARGADO
    if not YA_CARGADO:
        YA_CARGADO = True
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