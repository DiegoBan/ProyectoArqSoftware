import flet as ft
import json
from datetime import datetime
from soa_lib import send_message

def vista_ventas(page: ft.Page, sock, cambiar_vista_func):
    
    # --- Datos de Prueba Simulados (Catálogos del ERP) ---
    # En producción, pedirías esto al bus al cargar la vista
    PRODUCTOS_STOCK = {
        "Laptop HP": {"stock": 12, "precio_base": 750000},
        "Monitor Samsung 24\"": {"stock": 5, "precio_base": 130000},
        "Teclado Mecánico": {"stock": 0, "precio_base": 45000}, # Sin stock
        "Mouse Ergonómico": {"stock": 25, "precio_base": 25000}
    }
    
    CLIENTES_REGISTRADOS = [
        "Inversiones Alfa S.A.",
        "Juan Pérez Distribuidora",
        "Clínica Santa María",
        "Particular - María Pinto"
    ]

    # --- Campos del Recuadro de Cotización ---
    dropdown_cliente = ft.Dropdown(
        label="Seleccionar Cliente",
        width=350,
        options=[ft.dropdown.Option(cliente) for cliente in CLIENTES_REGISTRADOS]
    )

    dropdown_producto = ft.Dropdown(
        label="Seleccionar Producto",
        width=350,
        options=[ft.dropdown.Option(prod) for prod in PRODUCTOS_STOCK.keys()]
    )

    txt_cantidad = ft.TextField(
        label="Cantidad", 
        width=150, 
        value="1",
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string="")
    )

    # Campo de precio editable (solo números)
    txt_precio_final = ft.TextField(
        label="Precio Unitario Final ($)", 
        width=180,
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string="")
    )

    # Label dinámico para alertar sobre disponibilidad de inventario
    lbl_status_stock = ft.Text("", size=14, weight=ft.FontWeight.W_500)
    
    # Mostrar la fecha actual del sistema (Bloqueado para edición)
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    txt_fecha = ft.TextField(label="Fecha de Emisión", value=fecha_hoy, width=350, disabled=True)

    # --- Lógica de Validación de Stock en Tiempo Real ---
    def verificar_disponibilidad(e):
        prod_seleccionado = dropdown_producto.value
        cant_solicitada = txt_cantidad.value

        if not prod_seleccionado or not cant_solicitada:
            return

        cant_solicitada = int(cant_solicitada)
        stock_actual = PRODUCTOS_STOCK[prod_seleccionado]["stock"]
        precio_sugerido = PRODUCTOS_STOCK[prod_seleccionado]["precio_base"]

        # Auto-rellenar precio si está vacío
        if not txt_precio_final.value or e.control == dropdown_producto:
            txt_precio_final.value = str(precio_sugerido)

        if stock_actual == 0:
            lbl_status_stock.value = "❌ SIN STOCK DISPONIBLE"
            lbl_status_stock.color = ft.Colors.RED_400
        elif cant_solicitada > stock_actual:
            lbl_status_stock.value = f"⚠️ Stock insuficiente (Solo quedan {stock_actual} un.)"
            lbl_status_stock.color = ft.Colors.ORANGE_400
        else:
            lbl_status_stock.value = f"✅ Stock disponible ({stock_actual} un. en bodega)"
            lbl_status_stock.color = ft.Colors.GREEN_400
        
        page.update()

    # Vincular verificaciones a los eventos de cambio
    dropdown_producto.on_change = verificar_disponibilidad
    txt_cantidad.on_change = verificar_disponibilidad

    # --- Lógica de Envío de Cotización ---
    def btn_crear_cotizacion_click(e):
        if not dropdown_cliente.value or not dropdown_producto.value or not txt_precio_final.value:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, complete todos los parámetros"), bgcolor=ft.Colors.ORANGE_700)
            page.snack_bar.open = True
            page.update()
            return

        prod = dropdown_producto.value
        cant = int(txt_cantidad.value if txt_cantidad.value else 0)
        
        # Validar una última vez el stock antes de enviar al Bus
        if cant > PRODUCTOS_STOCK[prod]["stock"]:
            page.snack_bar = ft.SnackBar(ft.Text("No puedes procesar una venta sin stock suficiente"), bgcolor=ft.Colors.RED_700)
            page.snack_bar.open = True
            page.update()
            return

        payload = {
            "accion": "crear_cotizacion",
            "cliente": dropdown_cliente.value,
            "producto": prod,
            "cantidad": cant,
            "precio_total": cant * int(txt_precio_final.value),
            "fecha": txt_fecha.value
        }

        # Enviar al servicio de ventas ("venta")
        send_message(sock, "venta", json.dumps(payload))

        page.snack_bar = ft.SnackBar(ft.Text("Cotización generada y enviada con éxito"), bgcolor=ft.Colors.GREEN_700)
        page.snack_bar.open = True
        
        # Reset de interfaz
        dropdown_cliente.value = None
        dropdown_producto.value = None
        txt_cantidad.value = "1"
        txt_precio_final.value = ""
        lbl_status_stock.value = ""
        page.update()

    btn_generar = ft.Button("Generar Cotización", on_click=btn_crear_cotizacion_click, width=350, height=45)
    btn_volver = ft.TextButton("Volver al Dashboard", on_click=lambda _: cambiar_vista_func("dashboard"))

    # --- Estructura del Recuadro (Formulario) ---
    recuadro_cotizacion = ft.Column(
        controls=[
            ft.Text("Nueva Cotización", size=26, weight=ft.FontWeight.BOLD),
            ft.Text("Módulo de Ventas e Inventario", size=14, color=ft.Colors.GREY_400),
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            txt_fecha,
            dropdown_cliente,
            dropdown_producto,
            ft.Row(
                controls=[txt_cantidad, txt_precio_final],
                alignment=ft.MainAxisAlignment.CENTER,
                width=350
            ),
            lbl_status_stock,
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            btn_generar,
            btn_volver
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    return ft.Container(
        content=recuadro_cotizacion,
        alignment=ft.Alignment.CENTER,
        expand=True,
        padding=20
    )