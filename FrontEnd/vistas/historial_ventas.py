import flet as ft
import json
from datetime import datetime
from soa_lib import send_message

HISTORIAL_COTIZACIONES = [
    {
        "id": "COT-001",
        "cliente": "Inversiones Alfa S.A.",
        "producto": "Laptop HP",
        "cantidad": 2,
        "precio_total": 1500000,
        "fecha": "2026-06-01",
        "estado": "cotizado",
        "fecha_oco": "-"
    },
    {
        "id": "COT-002",
        "cliente": "Clínica Santa María",
        "producto": "Monitor Samsung 24\"",
        "cantidad": 5,
        "precio_total": 650000,
        "fecha": "2026-06-02",
        "estado": "oco",
        "fecha_oco": "2026-06-03"
    }
]

def vista_estado_cotizaciones(page: ft.Page, sock, cambiar_vista_func):
    global HISTORIAL_COTIZACIONES
    
    cotizacion_seleccionada = None

    lbl_detalle_titulo = ft.Text("Seleccione una cotización de la lista de abajo para gestionarla", size=14, color=ft.Colors.GREY_400)
    lbl_info_id = ft.Text("", size=16, weight=ft.FontWeight.BOLD)
    lbl_info_cliente = ft.Text("")
    lbl_info_producto = ft.Text("")
    lbl_info_total = ft.Text("")
    lbl_info_estado = ft.Text("")
    
    btn_actualizar = ft.ElevatedButton("Actualizar Estado", visible=False, bgcolor=ft.Colors.BLUE_700)

    def procesar_cambio_estado(e):
        nonlocal cotizacion_seleccionada
        if not cotizacion_seleccionada:
            return
            
        estado_actual = cotizacion_seleccionada["estado"]
        nuevo_estado = ""
        fecha_cambio = cotizacion_seleccionada["fecha_oco"]
        
        if estado_actual == "cotizado":
            nuevo_estado = "oco"
            fecha_cambio = datetime.now().strftime("%Y-%m-%d")
        elif estado_actual == "oco":
            nuevo_estado = "facturado"

        cotizacion_seleccionada["estado"] = nuevo_estado
        cotizacion_seleccionada["fecha_oco"] = fecha_cambio

        rut_operador_actual = page.session.store.get("rut")

        payload = {
            "accion": "actualizar_estado_cotizacion",
            "user": rut_operador_actual,
            "id": cotizacion_seleccionada["id"],
            "nuevo_estado": nuevo_estado,
            "fecha_oco": fecha_cambio
        }
        send_message(sock, "venta", json.dumps(payload))

        page.snack_bar = ft.SnackBar(ft.Text(f"Estado actualizado a {nuevo_estado.upper()}"), bgcolor=ft.Colors.GREEN_700)
        page.snack_bar.open = True

        cambiar_vista_func("estado_cotizaciones")

    btn_actualizar.on_click = procesar_cambio_estado

    def fila_seleccionada(cotizacion_dict):
        nonlocal cotizacion_seleccionada
        cotizacion_seleccionada = cotizacion_dict
        
        lbl_detalle_titulo.value = "Detalles del Documento Seleccionado:"
        lbl_info_id.value = f"ID: {cotizacion_dict['id']}"
        lbl_info_cliente.value = f"Cliente: {cotizacion_dict['cliente']}"
        lbl_info_producto.value = f"Items: {cotizacion_dict['cantidad']}x {cotizacion_dict['producto']}"
        lbl_info_total.value = f"Total: ${cotizacion_dict['precio_total']:,}"
        lbl_info_estado.value = f"Estado Actual: {cotizacion_dict['estado'].upper()}"
        
        if cotizacion_dict["estado"] == "cotizado":
            btn_actualizar.text = "Actualizar Estado a OCO"
            btn_actualizar.visible = True
        elif cotizacion_dict["estado"] == "oco":
            btn_actualizar.text = "Actualizar Estado a Facturado"
            btn_actualizar.visible = True
        else:
            btn_actualizar.visible = False
            
        page.update()

    cabecera_tabla = ft.Container(
        content=ft.Row([
            ft.Text("Acción", width=60, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
            ft.Text("ID", width=80, weight=ft.FontWeight.BOLD),
            ft.Text("Estado", width=90, weight=ft.FontWeight.BOLD),
            ft.Text("Cliente", width=180, weight=ft.FontWeight.BOLD),
            ft.Text("Cantidad / Producto", width=160, weight=ft.FontWeight.BOLD),
            ft.Text("Fecha Cot", width=90, weight=ft.FontWeight.BOLD),
            ft.Text("Fecha OCO", width=90, weight=ft.FontWeight.BOLD),
        ], alignment=ft.MainAxisAlignment.START),
        padding=10,
        bgcolor=ft.Colors.GREY_800,
        border_radius=5
    )

    lista_filas_controles = [cabecera_tabla]

    for cot in HISTORIAL_COTIZACIONES:
        def crear_evento_click(c=cot):
            return lambda _: fila_seleccionada(c)

        color_estado = ft.Colors.BLUE_400 if cot["estado"] == "cotizado" else ft.Colors.ORANGE_400 if cot["estado"] == "oco" else ft.Colors.GREEN_400

        fila_renderizada = ft.Container(
            content=ft.Row([
                ft.TextButton("Ver", width=60, on_click=crear_evento_click()),
                ft.Text(cot["id"], width=80),
                ft.Text(cot["estado"].upper(), width=90, weight=ft.FontWeight.BOLD, color=color_estado),
                ft.Text(cot["cliente"], width=180),
                ft.Text(f"{cot['cantidad']}x {cot['producto']}", width=160),
                ft.Text(cot["fecha"], width=90),
                ft.Text(cot["fecha_oco"], width=90),
            ], alignment=ft.MainAxisAlignment.START),
            padding=5,
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_800))
        )
        lista_filas_controles.append(fila_renderizada)

    panel_detalles = ft.Container(
        content=ft.Column([
            lbl_detalle_titulo,
            lbl_info_id,
            lbl_info_cliente,
            lbl_info_producto,
            lbl_info_total,
            lbl_info_estado
        ], spacing=5, tight=True),
        padding=15,
        bgcolor=ft.Colors.GREY_900,
        border_radius=8,
        width=380
    )

    panel_acciones = ft.Container(
        content=ft.Column([
            ft.Text("Acciones Disponibles", size=14, color=ft.Colors.GREY_400),
            ft.Divider(height=10, color=ft.Colors.GREY_700),
            btn_actualizar
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=15,
        bgcolor=ft.Colors.GREY_900,
        border_radius=8,
        width=240,
        height=160
    )

    btn_volver = ft.TextButton("Volver al Menú de Ventas", on_click=lambda _: cambiar_vista_func("ventas"))

    return ft.Container(
        content=ft.Column([
            ft.Text("Estado de Cotizaciones", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            ft.Row([panel_detalles, panel_acciones], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            ft.Divider(height=20, color=ft.Colors.GREY_800),
            ft.Text("Historial de Documentos Registrados:", size=12, color=ft.Colors.GREY_400),
            ft.Column(controls=lista_filas_controles, spacing=0, expand=True),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            btn_volver
        ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=15,
        expand=True
    )