import flet as ft
import json
from datetime import datetime
from soa_lib import send_message

CLIENTES_PARA_COT = None   
PRODUCTOS_PARA_COT = None


def vista_nueva_cotizacion(page: ft.Page, sock, cambiar_vista_func):
    global CLIENTES_PARA_COT, PRODUCTOS_PARA_COT

    clientes = CLIENTES_PARA_COT or []
    productos = PRODUCTOS_PARA_COT or []
    datos_listos = CLIENTES_PARA_COT is not None and PRODUCTOS_PARA_COT is not None

    txt_cot = ft.TextField(label="Número de Cotización (COT)", width=350)
    txt_cantidad = ft.TextField(label="Cantidad", width=150, value="1")
    txt_precio_final = ft.TextField(label="Precio Unit. ($)", width=180)
    txt_fecha = ft.TextField(
        label="Fecha de Emisión",
        value=datetime.now().strftime("%Y-%m-%d"),
        width=350,
        disabled=True
    )

    dropdown_cliente = ft.Dropdown(
        label="Seleccionar Cliente" if clientes else "⏳ Cargando clientes...",
        width=350,
        disabled=not clientes,
        options=[ft.dropdown.Option(key=str(c["id"]), text=c["nombre"]) for c in clientes]
    )

    dropdown_producto = ft.Dropdown(
        label="Seleccionar Producto" if productos else "⏳ Cargando productos...",
        width=350,
        disabled=not productos,
        options=[ft.dropdown.Option(key=str(p["id"]), text=p["nombre"]) for p in productos]
    )

    btn_generar = ft.ElevatedButton(
        "Generar Cotización",
        width=350,
        height=45,
        bgcolor=ft.Colors.BLUE_700 if datos_listos else ft.Colors.GREY_700,
        disabled=not datos_listos
    )

    def btn_crear_cotizacion_click(e):
        if not txt_cot.value or not dropdown_cliente.value or not dropdown_producto.value \
                or not txt_precio_final.value or not txt_cantidad.value:
            page.overlay.append(ft.SnackBar(ft.Text("Complete todos los campos"), bgcolor=ft.Colors.ORANGE_700))
            page.overlay[-1].open = True
            page.update()
            return

        payload = {
            "accion": "crear_cot",
            "COT": int(txt_cot.value),
            "id_cliente": int(dropdown_cliente.value),
            "fecha_cot": txt_fecha.value,
            "productos": [{
                "id_producto": int(dropdown_producto.value),
                "cantidad": int(txt_cantidad.value),
                "precio_unitario": int(txt_precio_final.value)
            }]
        }

        btn_generar.text = "Guardando..."
        btn_generar.disabled = True
        if page.controls:
            page.controls[0].disabled = True
        page.update()

        # Solo enviamos. main.py procesa la respuesta en escuchar_bus().
        send_message(sock, "manej", json.dumps(payload))

    btn_generar.on_click = btn_crear_cotizacion_click

    # Si los datos aún no están cargados, pedirlos al bus.
    # main.py recibirá ambas respuestas y reconstruirá esta vista con los datos.
    if CLIENTES_PARA_COT is None:
        send_message(sock, "clien", json.dumps({
            "accion": "obtener_clientes",
            "user_rut": page.session.store.get("rut")
        }))
    if PRODUCTOS_PARA_COT is None:
        send_message(sock, "produ", json.dumps({"accion": "obtener_productos"}))

    def salir_de_vista(e):
        global CLIENTES_PARA_COT, PRODUCTOS_PARA_COT
        # 1. Vaciamos las variables para que la próxima vez pida datos frescos
        CLIENTES_PARA_COT = None
        PRODUCTOS_PARA_COT = None
        # 2. Cambiamos de vista
        cambiar_vista_func("ventas")

    btn_volver = ft.TextButton(
        "Volver al Menú de Ventas",
        on_click=salir_de_vista
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Nueva Cotización", size=26, weight=ft.FontWeight.BOLD),
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                txt_fecha, txt_cot, dropdown_cliente, dropdown_producto,
                ft.Row([txt_cantidad, txt_precio_final],
                       alignment=ft.MainAxisAlignment.CENTER, width=350),
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                btn_generar, btn_volver
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO
        ),
        alignment=ft.Alignment.CENTER,
        expand=True,
        padding=20
    )