import flet as ft
import json
from datetime import datetime
from soa_lib import send_message

# Diccionario global en Python para simular la base de datos de cotizaciones
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
    
    # Cotización actualmente seleccionada para el panel superior
    cotizacion_seleccionada = None

    # --- Elementos del Panel de Detalles Superior ---
    lbl_detalle_titulo = ft.Text("Seleccione una cotización de la tabla para gestionarla", size=14, color=ft.Colors.GREY_400)
    lbl_info_id = ft.Text("", size=16, weight=ft.FontWeight.BOLD)
    lbl_info_cliente = ft.Text("")
    lbl_info_producto = ft.Text("")
    lbl_info_total = ft.Text("")
    lbl_info_estado = ft.Text("")
    
    btn_actualizar = ft.ElevatedButton("Actualizar Estado", visible=False, bgcolor=ft.Colors.BLUE_700)

    # --- Lógica de Actualización de Estado ---
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

        # 1. Actualizar en nuestra memoria local de Python
        cotizacion_seleccionada["estado"] = nuevo_estado
        cotizacion_seleccionada["fecha_oco"] = fecha_cambio

        # 2. Despachar notificación al bus SOA
        payload = {
            "accion": "actualizar_estado_cotizacion",
            "id": cotizacion_seleccionada["id"],
            "nuevo_estado": nuevo_estado,
            "fecha_oco": fecha_cambio
        }
        send_message(sock, "venta", json.dumps(payload))

        # 3. Mostrar Snack Bar de éxito
        page.snack_bar = ft.SnackBar(ft.Text(f"Estado actualizado a {nuevo_estado.upper()}"), bgcolor=ft.Colors.GREEN_700)
        page.snack_bar.open = True

        # 4. Forzar redibujado completo de la interfaz para refrescar la tabla excel
        cambiar_vista_func("estado_cotizaciones")

    btn_actualizar.on_click = procesar_cambio_estado

    # --- Lógica al Seleccionar una Fila de la Tabla ---
    def fila_seleccionada(cotizacion_dict):
        nonlocal cotizacion_seleccionada
        cotizacion_seleccionada = cotizacion_dict
        
        lbl_detalle_titulo.value = "Detalles del Documento Seleccionado:"
        lbl_info_id.value = f"ID: {cotizacion_dict['id']}"
        lbl_info_cliente.value = f"Cliente: {cotizacion_dict['cliente']}"
        lbl_info_producto.value = f"Items: {cotizacion_dict['cantidad']}x {cotizacion_dict['producto']}"
        lbl_info_total.value = f"Total: ${cotizacion_dict['precio_total']:,}"
        lbl_info_estado.value = f"Estado Actual: {cotizacion_dict['estado'].upper()}"
        
        # Configurar dinámicamente el botón de transición de estados
        if cotizacion_dict["estado"] == "cotizado":
            btn_actualizar.text = "Actualizar Estado a OCO"
            btn_actualizar.visible = True
        elif cotizacion_dict["estado"] == "oco":
            btn_actualizar.text = "Actualizar Estado a Facturado"
            btn_actualizar.visible = True
        else:
            btn_actualizar.visible = False # Si ya está facturado, no se puede avanzar más
            
        page.update()

    # --- Construcción de la Tabla tipo Excel ---
    tabla_excel = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Estado")),
            ft.DataColumn(ft.Text("Cliente")),
            ft.DataColumn(ft.Text("Cantidad / Prod")),
            ft.DataColumn(ft.Text("Fecha Cot")),
            ft.DataColumn(ft.Text("Fecha OCO")),
        ],
        rows=[]
    )

    # Rellenar la tabla dinámicamente desde el historial global
    for cot in HISTORIAL_COTIZACIONES:
        # Truco nativo para capturar el contexto de la fila al hacer click
        def crear_evento_click(c=cot):
            return lambda _: fila_seleccionada(c)

        tabla_excel.rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(cot["id"])),
                    ft.DataCell(ft.Text(cot["estado"].upper(), weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400 if cot["estado"]=="cotizado" else ft.Colors.ORANGE_400 if cot["estado"]=="oco" else ft.Colors.GREEN_400)),
                    ft.DataCell(ft.Text(cot["cliente"])),
                    ft.DataCell(ft.Text(f"{cot['cantidad']}x {cot['producto']}")),
                    ft.DataCell(ft.Text(cot["fecha"])),
                    ft.DataCell(ft.Text(cot["fecha_oco"])),
                ],
                on_select_changed=crear_evento_click()
            )
        )

    # --- Maquetación de los Paneles ---
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
        width=350
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
        width=250,
        height=160
    )

    bloque_superior = ft.Row(
        [panel_detalles, panel_acciones],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )

    btn_volver = ft.TextButton("Volver al Menú de Ventas", on_click=lambda _: cambiar_vista_func("ventas"))

    # --- Render Global ---
    return ft.Container(
        content=ft.Column([
            ft.Text("Estado de Cotizaciones", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            bloque_superior,
            ft.Divider(height=20, color=ft.Colors.GREY_800),
            ft.Text("Historial de Documentos Registrados (Haga click en una fila para gestionar):", size=12, color=ft.Colors.GREY_400),
            ft.ListView([tabla_excel], expand=True, spacing=10, height=250),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            btn_volver
        ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=15,
        expand=True
    )