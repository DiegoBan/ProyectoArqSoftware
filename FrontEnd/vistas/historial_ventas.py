import flet as ft
import json
from datetime import datetime
from soa_lib import send_message

def vista_estado_cotizaciones(page: ft.Page, sock, cambiar_vista_func):
    
    # 1. SOLICITAR LOS DATOS AL BACKEND AL CARGAR LA VISTA
    lista_cotizaciones = []
    try:
        # Asumo que envías la acción sin un ID específico para que el backend traiga todas
        payload_peticion = {"accion": "ver_detalles"}
        
        # En la mayoría de implementaciones SOA de este tipo, send_message retorna la respuesta del bus.
        # Si tu librería requiere un sock.recv() extra, agrégalo aquí.
        respuesta_raw = send_message(sock, "venta", json.dumps(payload_peticion)) 
        
        if respuesta_raw:
            respuesta_json = json.loads(respuesta_raw)
            if respuesta_json.get("estado") == "ok":
                lista_cotizaciones = respuesta_json.get("detalles", [])
    except Exception as e:
        print(f"Error al cargar historial desde el bus: {e}")
        # Puedes mostrar un SnackBar aquí si lo deseas para notificar el error de conexión.

    cotizacion_seleccionada = None

    # Etiquetas del panel de detalles (ahora extendidas para mostrar TODA la info)
    lbl_detalle_titulo = ft.Text("Seleccione una cotización de la lista de abajo para gestionarla", size=14, color=ft.Colors.GREY_400)
    lbl_info_id = ft.Text("", size=16, weight=ft.FontWeight.BOLD)
    lbl_info_cliente = ft.Text("")
    lbl_info_producto = ft.Text("")
    lbl_info_fechas = ft.Text("")
    lbl_info_oco = ft.Text("")
    lbl_info_factura = ft.Text("")
    lbl_info_guia = ft.Text("")
    lbl_info_total = ft.Text("", weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
    lbl_info_estado = ft.Text("")
    
    txt_orden_compra = ft.TextField(label="Orden de Compra", visible=False, height=45, text_size=13)
    txt_nota_venta = ft.TextField(label="Nota de Venta (Número)", visible=False, height=45, text_size=13, input_filter=ft.NumbersOnlyInputFilter())
    txt_num_factura = ft.TextField(label="N° Factura", visible=False, height=45, text_size=13, input_filter=ft.NumbersOnlyInputFilter())

    btn_actualizar = ft.ElevatedButton("Actualizar Estado", visible=False, bgcolor=ft.Colors.BLUE_700, width=200)

    def procesar_cambio_estado(e):
        nonlocal cotizacion_seleccionada
        if not cotizacion_seleccionada:
            return
            
        estado_actual = str(cotizacion_seleccionada.get("estado", "")).lower()
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        
        # ACTUALIZAR DE COTIZADO A OCO
        if estado_actual == "cotizado":
            if not txt_orden_compra.value or not txt_nota_venta.value:
                page.snack_bar = ft.SnackBar(ft.Text("Debe ingresar la Orden de Compra y la Nota de Venta"), bgcolor=ft.Colors.RED_700)
                page.snack_bar.open = True
                page.update()
                return

            payload = {
                "accion": "act_cot",
                "COT": cotizacion_seleccionada["COT"],
                "orden_de_compra": txt_orden_compra.value,
                "fecha_oco": fecha_actual,
                "nota_de_venta": int(txt_nota_venta.value)
            }

        # ACTUALIZAR DE OCO A FACTURADO
        elif estado_actual == "oco":
            if not txt_num_factura.value:
                page.snack_bar = ft.SnackBar(ft.Text("Debe ingresar el Número de Factura"), bgcolor=ft.Colors.RED_700)
                page.snack_bar.open = True
                page.update()
                return
            
            payload = {
                "accion": "act_cot",
                "COT": cotizacion_seleccionada["COT"],
                "facturas": [
                    {
                        "numero_factura": int(txt_num_factura.value),
                        "fecha": fecha_actual,
                        "productos": [
                            {
                                "id_producto": cotizacion_seleccionada.get("id_producto", 1), # Asegúrate de que el backend envíe el id_producto también
                                "cantidad": cotizacion_seleccionada.get("cantidad", 0)
                            }
                        ]
                    }
                ]
            }

        # Enviar actualización al bus SOA
        send_message(sock, "venta", json.dumps(payload))
        page.snack_bar = ft.SnackBar(ft.Text(f"¡Cotización {cotizacion_seleccionada['COT']} actualizada exitosamente!"), bgcolor=ft.Colors.GREEN_700)
        page.snack_bar.open = True
        
        # Refrescar la vista para volver a cargar los datos desde la BD
        cambiar_vista_func("estado_cotizaciones")

    btn_actualizar.on_click = procesar_cambio_estado

    def fila_seleccionada(cot):
        nonlocal cotizacion_seleccionada
        cotizacion_seleccionada = cot
        
        # Función auxiliar para manejar los nulls de la base de datos
        def seguro(valor, sufijo="", prefijo=""):
            return f"{prefijo}{valor}{sufijo}" if valor is not None else "N/A"

        # Cálculo del total
        cantidad = cot.get('cantidad', 0)
        precio = cot.get('precio_unitario', 0)
        total = cantidad * precio

        # Llenado de toda la información en el panel
        lbl_detalle_titulo.value = "Detalles del Documento Seleccionado:"
        lbl_info_id.value = f"COT: {cot.get('COT', 'ERROR')}"
        lbl_info_cliente.value = f"Cliente: {cot.get('nombre_cliente', 'N/A')}"
        lbl_info_producto.value = f"Producto: {cantidad}x {cot.get('nombre', 'N/A')} (PN: {seguro(cot.get('PN'))})"
        lbl_info_fechas.value = f"Creado: {seguro(cot.get('fecha_creacion'))[:10]} | Fecha COT: {seguro(cot.get('fecha_cot'))}"
        lbl_info_oco.value = f"OC: {seguro(cot.get('orden_de_compra'))} | Nota Venta: {seguro(cot.get('nota_de_venta'))} | Fecha: {seguro(cot.get('fecha_oco'))}"
        lbl_info_factura.value = f"Factura: {seguro(cot.get('numero_factura'))} | Estado: {seguro(cot.get('estado_factura'))}"
        lbl_info_guia.value = f"Guía Despacho: {seguro(cot.get('numero_guia'))} | Cant. Entregada: {seguro(cot.get('cantidad_guia'))}"
        lbl_info_total.value = f"Total Línea: ${total:,}"
        
        estado = str(cot.get('estado', '')).lower()
        lbl_info_estado.value = f"Estado Actual: {estado.upper()}"
        
        # Lógica visual de inputs
        txt_orden_compra.visible = False
        txt_nota_venta.visible = False
        txt_num_factura.visible = False
        btn_actualizar.visible = False

        if estado == "cotizado":
            txt_orden_compra.visible = True
            txt_nota_venta.visible = True
            btn_actualizar.text = "Actualizar a OCO"
            btn_actualizar.visible = True
        elif estado == "oco":
            txt_num_factura.visible = True
            btn_actualizar.text = "Actualizar a FACTURADO"
            btn_actualizar.visible = True
            
        page.update()

    cabecera_tabla = ft.Container(
        content=ft.Row([
            ft.Text("Acción", width=60, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
            ft.Text("COT", width=60, weight=ft.FontWeight.BOLD),
            ft.Text("Estado", width=90, weight=ft.FontWeight.BOLD),
            ft.Text("Cliente", width=160, weight=ft.FontWeight.BOLD),
            ft.Text("Cantidad / Producto", width=180, weight=ft.FontWeight.BOLD),
            ft.Text("OC", width=90, weight=ft.FontWeight.BOLD),
            ft.Text("Factura", width=70, weight=ft.FontWeight.BOLD),
        ], alignment=ft.MainAxisAlignment.START),
        padding=10,
        bgcolor=ft.Colors.GREY_800,
        border_radius=5
    )

    lista_filas_controles = [cabecera_tabla]

    # 2. DIBUJAR LAS FILAS CON LOS DATOS REALES DEL BACKEND
    for cot in lista_cotizaciones:
        def crear_evento_click(c=cot):
            return lambda _: fila_seleccionada(c)

        estado = str(cot.get("estado", "")).lower()
        color_estado = ft.Colors.BLUE_400 if estado == "cotizado" else ft.Colors.ORANGE_400 if estado == "oco" else ft.Colors.GREEN_400

        # Manejo de nulls para la tabla
        oc_str = str(cot.get("orden_de_compra")) if cot.get("orden_de_compra") is not None else "-"
        fac_str = str(cot.get("numero_factura")) if cot.get("numero_factura") is not None else "-"

        fila_renderizada = ft.Container(
            content=ft.Row([
                ft.TextButton("Ver", width=60, on_click=crear_evento_click()),
                ft.Text(str(cot.get("COT", "N/A")), width=60),
                ft.Text(estado.upper(), width=90, weight=ft.FontWeight.BOLD, color=color_estado),
                ft.Text(str(cot.get("nombre_cliente", "N/A"))[:15], width=160), # Cortamos texto largo
                ft.Text(f"{cot.get('cantidad', 0)}x {str(cot.get('nombre', 'N/A'))[:15]}", width=180),
                ft.Text(oc_str, width=90),
                ft.Text(fac_str, width=70),
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
            ft.Divider(height=10, color=ft.Colors.GREY_700),
            lbl_info_fechas,
            lbl_info_oco,
            lbl_info_factura,
            lbl_info_guia,
            ft.Divider(height=10, color=ft.Colors.GREY_700),
            lbl_info_estado
        ], spacing=5, tight=True),
        padding=15,
        bgcolor=ft.Colors.GREY_900,
        border_radius=8,
        width=450 # Amplié el panel para que quepa toda la información
    )

    panel_acciones = ft.Container(
        content=ft.Column([
            ft.Text("Datos Requeridos", size=14, color=ft.Colors.GREY_400),
            ft.Divider(height=10, color=ft.Colors.GREY_700),
            txt_orden_compra,
            txt_nota_venta,
            txt_num_factura,
            btn_actualizar
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=15,
        bgcolor=ft.Colors.GREY_900,
        border_radius=8,
        width=260
    )

    btn_volver = ft.TextButton("Volver al Menú de Ventas", on_click=lambda _: cambiar_vista_func("ventas"))

    return ft.Container(
        content=ft.Column([
            ft.Text("Gestión de Cotizaciones", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            ft.Row([panel_detalles, panel_acciones], alignment=ft.MainAxisAlignment.CENTER, spacing=20, vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Divider(height=20, color=ft.Colors.GREY_800),
            ft.Text("Historial de Documentos Registrados:", size=12, color=ft.Colors.GREY_400),
            ft.Column(controls=lista_filas_controles, spacing=0, expand=True, scroll=ft.ScrollMode.AUTO),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            btn_volver
        ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=15,
        expand=True
    )