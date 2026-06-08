import flet as ft
import json
import asyncio
from datetime import datetime
from soa_lib import send_message, receive_message # <--- ¡IMPORTANTE: Agrega receive_message aquí!

def vista_nueva_cotizacion(page: ft.Page, sock, cambiar_vista_func):
    
    txt_cot = ft.TextField(label="Número de Cotización (COT)", width=350)
    txt_cantidad = ft.TextField(label="Cantidad", width=150, value="1")
    txt_precio_final = ft.TextField(label="Precio Unit. ($)", width=180)
    txt_fecha = ft.TextField(label="Fecha de Emisión", value=datetime.now().strftime("%Y-%m-%d"), width=350, disabled=True)

    dropdown_cliente = ft.Dropdown(label="⏳ Cargando clientes desde el bus...", width=350, disabled=True)
    dropdown_producto = ft.Dropdown(label="⏳ Cargando productos desde el bus...", width=350, disabled=True)
    btn_generar = ft.ElevatedButton("Generar Cotización", width=350, height=45, bgcolor=ft.Colors.GREY_700, disabled=True)

    # ---------------------------------------------------------
    # LA FUNCIÓN CORREGIDA USANDO TU PROTOCOLO SOA
    # ---------------------------------------------------------
    def pedir_datos_bloqueantes():
        import time
        clientes, productos = [], []
        
        try:
            sock.settimeout(5.0) 
            
            # --- PEDIR CLIENTES ---
            send_message(sock, "clien", json.dumps({"accion": "obtener_clientes"}))
            # Usamos TU función para recibir y limpiar el mensaje
            resp_c_raw = receive_message(sock) 
            print(resp_c_raw)
            
            if resp_c_raw:
                try:
                    clientes = json.loads(resp_c_raw).get("clientes", [])
                except json.JSONDecodeError:
                    print(f"Error decodificando Clientes: {resp_c_raw}")
                    
            time.sleep(0.2) # Pequeña pausa por seguridad en la red
            
            # --- PEDIR PRODUCTOS ---
            send_message(sock, "produ", json.dumps({"accion": "obtener_productos"}))
            # Usamos TU función de nuevo
            resp_p_raw = receive_message(sock) 
            
            if resp_p_raw:
                try:
                    productos = json.loads(resp_p_raw).get("productos", [])
                except json.JSONDecodeError:
                    print(f"Error decodificando Productos: {resp_p_raw}")
                
        except Exception as e:
            print(f"Error al comunicar con el bus SOA: {e}")
        finally:
            sock.settimeout(None)
            
        return clientes, productos

    async def cargar_datos_async():
        datos_clientes, datos_productos = await asyncio.to_thread(pedir_datos_bloqueantes)
        
        if datos_clientes:
            dropdown_cliente.options = [ft.dropdown.Option(key=str(c["id"]), text=c["nombre"]) for c in datos_clientes]
            dropdown_cliente.label = "Seleccionar Cliente"
            dropdown_cliente.disabled = False
        else:
            dropdown_cliente.label = "⚠ Error al cargar clientes"

        if datos_productos:
            dropdown_producto.options = [ft.dropdown.Option(key=str(p["id"]), text=p["nombre"]) for p in datos_productos]
            dropdown_producto.label = "Seleccionar Producto"
            dropdown_producto.disabled = False
            
        if datos_clientes and datos_productos:
            btn_generar.disabled = False 
            btn_generar.bgcolor = ft.Colors.BLUE_700

        page.update() 

    # ---------------------------------------------------------
    # BOTÓN CREAR COTIZACIÓN
    # ---------------------------------------------------------
    def crear_cotizacion_bloqueante(payload):
        # También usamos receive_message aquí para atrapar la confirmación del bus
        send_message(sock, "venta", json.dumps(payload))
        return receive_message(sock)

    async def btn_crear_cotizacion_click(e):
        if not txt_cot.value or not dropdown_cliente.value or not dropdown_producto.value or not txt_precio_final.value or not txt_cantidad.value:
            page.snack_bar = ft.SnackBar(ft.Text("Complete todos los campos"), bgcolor=ft.Colors.ORANGE_700)
            page.snack_bar.open = True
            page.update()
            return

        payload = {
            "accion": "crear_cot",
            "COT": int(txt_cot.value),
            "id_cliente": int(dropdown_cliente.value),
            "fecha_cot": txt_fecha.value,
            "productos": [{"id_producto": int(dropdown_producto.value), "cantidad": int(txt_cantidad.value), "precio_unitario": int(txt_precio_final.value)}]
        }
        
        try:
            btn_generar.text = "Guardando en BD..."
            btn_generar.disabled = True
            page.update()

            respuesta_backend = await asyncio.to_thread(crear_cotizacion_bloqueante, payload)
            print("El backend respondió:", respuesta_backend)
            
            page.snack_bar = ft.SnackBar(ft.Text("Cotización generada exitosamente"), bgcolor=ft.Colors.GREEN_700)
            page.snack_bar.open = True
            cambiar_vista_func("ventas")
            
        except Exception as error:
            btn_generar.text = "Generar Cotización"
            btn_generar.disabled = False
            page.snack_bar = ft.SnackBar(ft.Text("Error al guardar en la base de datos"), bgcolor=ft.Colors.RED_700)
            page.snack_bar.open = True
            page.update()

    btn_generar.on_click = btn_crear_cotizacion_click
    btn_volver = ft.TextButton("Volver al Menú de Ventas", on_click=lambda _: cambiar_vista_func("ventas"))

    # ---------------------------------------------------------
    # RENDERIZADO VISUAL
    # ---------------------------------------------------------
    recuadro_cotizacion = ft.Column(
        controls=[
            ft.Text("Nueva Cotización", size=26, weight=ft.FontWeight.BOLD),
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            txt_fecha, txt_cot, dropdown_cliente, dropdown_producto,
            ft.Row([txt_cantidad, txt_precio_final], alignment=ft.MainAxisAlignment.CENTER, width=350),
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            btn_generar, btn_volver
        ],
        alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO
    )

    page.run_task(cargar_datos_async)

    return ft.Container(content=recuadro_cotizacion, alignment=ft.Alignment.CENTER, expand=True, padding=20)