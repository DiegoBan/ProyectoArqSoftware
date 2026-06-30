import flet as ft
import json
import hashlib
from soa_lib import send_message

# FIX: esta vista antes hacía su propia llamada bloqueante a receive_message(sock)
# DENTRO de btn_ingresar_click, mientras main.py ya tiene un hilo (escuchar_bus)
# leyendo continuamente del MISMO socket. Dos hilos haciendo recv() sobre el mismo
# socket TCP compiten por los bytes: cualquiera de los dos puede robarse parte de
# un mensaje, dejando al otro con basura ("Expecting value: li..." era literalmente
# la mitad de un mensaje cortado a la mitad por la carrera entre hilos).
#
# Solución: el login ahora SOLO envía el mensaje al bus (igual que clientes.py y
# empleados.py). La respuesta la procesa main.py en escuchar_bus, que ya detecta
# "usuario" in respuesta y llama cambiar_vista("dashboard") automáticamente.

def vista_login(page: ft.Page, sock, cambiar_vista_func):
    # --- Definición de Campos ---
    txt_email = ft.TextField(label="Email", width=350)
    txt_password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=350)

    btn_ingresar = ft.ElevatedButton("Iniciar Sesión", width=350, height=45, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)

    def btn_ingresar_click(e):
        if not txt_email.value or not txt_password.value:
            alerta_vacio = ft.SnackBar(ft.Text("Por favor, ingresa tu email y contraseña"), bgcolor=ft.Colors.ORANGE_700)
            page.overlay.append(alerta_vacio)
            alerta_vacio.open = True
            page.update()
            return

        # Generar el Hash SHA-256
        password_bytes = txt_password.value.encode('utf-8')
        password_hasheada = hashlib.sha256(password_bytes).hexdigest()

        payload = {
            "accion": "iniciar_sesion",
            "email": txt_email.value,
            "password_hash": password_hasheada
        }

        # Estado visual de carga
        btn_ingresar.text = "Autenticando..."
        btn_ingresar.disabled = True
        page.update()

        # FIX: solo enviamos. La respuesta la procesa escuchar_bus() en main.py,
        # que llama cambiar_vista("dashboard") si el login fue exitoso, o
        # muestra el snackbar de error y rehabilita la UI si no lo fue.
        send_message(sock, "usuar", json.dumps(payload))

    btn_ingresar.on_click = btn_ingresar_click

    formulario = ft.Column(
        controls=[
            ft.Text("Iniciar Sesión", size=30, weight=ft.FontWeight.BOLD),
            ft.Text("Sistema ERP Síncrono", size=14, color=ft.Colors.GREY_400),
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
        alignment=ft.Alignment.CENTER,
        expand=True,
        padding=20
    )