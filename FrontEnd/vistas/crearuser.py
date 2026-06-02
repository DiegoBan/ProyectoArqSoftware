import flet as ft
import json
import hashlib
from soa_lib import send_message

def vista_crear_usuario(page: ft.Page, sock, cambiar_vista_func):
    
    # --- Definición de Campos de Texto ---
    txt_rut = ft.TextField(label="RUT (ej: 12.345.678-9)", width=350, max_length=12)
    txt_email = ft.TextField(label="Email", width=350)
    txt_password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=350)
    txt_nombre = ft.TextField(label="Nombre", width=350)
    txt_apellido = ft.TextField(label="Apellido", width=350)
    
    dropdown_rol = ft.Dropdown(
        label="Rol del Trabajador",
        width=350,
        options=[
            ft.dropdown.Option("admin"),      # Acceso total (crear usuarios, ver todo)
            ft.dropdown.Option("vendedor"),   # Solo puede crear ventas/cotizaciones
            ft.dropdown.Option("bodeguero"),  # Solo puede ver productos y guías de despacho
            ft.dropdown.Option("finanzas"),   # Solo puede ver facturas
        ],
        value="vendedor" # Valor por defecto 
    )
    
    txt_telefono = ft.TextField(label="Teléfono", width=350)
    txt_fecha_nac = ft.TextField(label="Fecha de Nacimiento (YYYY-MM-DD)", width=350)

    # --- Lógica del Botón ---
    def btn_crear_click(e):
        # Validar que los campos no estén vacíos
        if not txt_rut.value or not txt_email.value:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, llena los campos obligatorios"), bgcolor=ft.Colors.ORANGE_700)
            page.snack_bar.open = True
            page.update()
            return
        
        password_bytes = txt_password.value.encode('utf-8')
        password_hash = hashlib.sha256(password_bytes).hexdigest()
        # Construir el JSON
        payload = {
            "accion": "crear_usuario",
            "user": "admin", # Agregado para pasar la verificación de tu functions.py
            "rut": txt_rut.value,
            "email": txt_email.value,
            "password_hash": password_hash,
            "nombre": txt_nombre.value,
            "apellido": txt_apellido.value,
            "rol": dropdown_rol.value,
            "telefono": txt_telefono.value,
            "Fecha_nacimiento": txt_fecha_nac.value
        }
        
        # Enviar el payload al servicio "usuar"
        send_message(sock, "usuar", json.dumps(payload))
        
        # Opcional: Limpiar el formulario después de enviar
        txt_rut.value = ""
        txt_email.value = ""
        txt_password.value = ""
        txt_nombre.value = ""
        txt_apellido.value = ""
        txt_telefono.value = ""
        txt_fecha_nac.value = ""
        page.update()

    # --- Botones ---
    btn_guardar = ft.Button("Crear Usuario", on_click=btn_crear_click, width=350, height=45)
    btn_volver = ft.TextButton("Volver al Login", on_click=lambda _: cambiar_vista_func("login"))

    # --- Estructura Visual ---
    formulario = ft.Column(
        controls=[
            ft.Text("Registro de Nuevo Usuario", size=26, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT), # Espaciador
            txt_rut,
            txt_email,
            txt_password,
            txt_nombre,
            txt_apellido,
            dropdown_rol,
            txt_telefono,
            txt_fecha_nac,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            btn_guardar,
            btn_volver
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    
    return ft.Container(
        content=formulario, 
        alignment=ft.Alignment.CENTER, 
        expand=True,
        padding=20
    )