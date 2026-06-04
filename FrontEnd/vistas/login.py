import flet as ft
import json
import hashlib
from soa_lib import send_message

def vista_login(page: ft.Page, sock):
    
    # --- Definición de Campos ---
    txt_email = ft.TextField(label="Email", width=350)
    txt_password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=350)

    # --- Lógica del Botón ---
    def btn_ingresar_click(e):
        if not txt_email.value or not txt_password.value:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, ingresa tu email y contraseña"), bgcolor=ft.Colors.ORANGE_700)
            page.snack_bar.open = True
            page.update()
            return

        # Generar el Hash SHA-256
        password_bytes = txt_password.value.encode('utf-8')
        password_hasheada = hashlib.sha256(password_bytes).hexdigest()

        # Construir el JSON
        payload = {
            "accion": "iniciar_sesion",
            "email": txt_email.value,
            "password_hash": password_hasheada
        }
        
        # Enviar al servicio
        send_message(sock, "usuar", json.dumps(payload))
        
        # Desactivar temporalmente el botón para evitar spam
        btn_ingresar.disabled = True
        page.update()

    # --- Botón Único ---
    btn_ingresar = ft.Button("Iniciar Sesión", on_click=btn_ingresar_click, width=350, height=45)

    # --- Estructura Visual ---
    formulario = ft.Column(
        controls=[
            ft.Text("Iniciar Sesión", size=30, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            txt_email,
            txt_password,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            btn_ingresar
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    
    return ft.Container(
        content=formulario, 
        alignment=ft.Alignment(0, 0), 
        expand=True,
        padding=20
    )