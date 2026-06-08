import flet as ft
import json
import hashlib
from soa_lib import send_message, receive_message

# Importante: Añadimos 'cambiar_vista_func' como parámetro
def vista_login(page: ft.Page, sock, cambiar_vista_func):
    if sock:
        print("Si hay socker")
    else:
        print("No hay socket")
    
    # --- Definición de Campos ---
    txt_email = ft.TextField(label="Email", width=350)
    txt_password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=350)

    # El botón se declara aquí para poder modificarlo adentro de la función
    btn_ingresar = ft.ElevatedButton("Iniciar Sesión", width=350, height=45, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)

    # --- El "Cazador" de JSON para limpiar la basura del bus ---
    def atrapar_json(respuesta_cruda):
        if not respuesta_cruda:
            return ""
        texto = respuesta_cruda.decode('utf-8') if isinstance(respuesta_cruda, bytes) else str(respuesta_cruda)
        inicio = texto.find('{')
        if inicio != -1:
            json_puro = texto[inicio:]
            if '}{' in json_puro:
                return json_puro.split('}{')[0] + '}'
            return json_puro
        return ""

    # --- Lógica del Botón ---
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

        # Construir el JSON
        payload = {
            "accion": "iniciar_sesion",
            "email": txt_email.value,
            "password_hash": password_hasheada
        }
        
        try:
            # Estado visual de carga
            btn_ingresar.text = "Autenticando..."
            btn_ingresar.disabled = True
            page.update()

            # --- Comunicación bloqueante con el Bus ---
            sock.settimeout(5.0)
            send_message(sock, "usuar", json.dumps(payload))
            respuesta_cruda = receive_message(sock)
            print("esta es la respuesta", respuesta_cruda)

            # Limpiamos el JSON
            texto_limpio = atrapar_json(respuesta_cruda)
            
            if not texto_limpio:
                raise ValueError("No se recibió respuesta válida del bus")

            respuesta_json = json.loads(texto_limpio)

            # --- Manejo de la Respuesta ---
            if respuesta_json.get("estado") == "ok":
                usuario = respuesta_json.get("usuario", {})
                
                # Guardamos las variables de sesión en Flet
                page.session.store.set("rol", str(usuario.get("rol", ""))) 
                page.session.store.set("nombre", str(usuario.get("nombre", "")))
                page.session.store.set("rut", str(usuario.get("rut", "")))
                
                page.snack_bar = ft.SnackBar(ft.Text("¡Acceso Concedido!"), bgcolor=ft.Colors.GREEN_700)
                page.snack_bar.open = True
                
                # Vamos al Dashboard principal
                cambiar_vista_func("dashboard")
                
            else:
                # Caso de Credenciales Inválidas
                mensaje_error = respuesta_json.get("mensaje", "Credenciales incorrectas")
                page.snack_bar = ft.SnackBar(ft.Text(mensaje_error), bgcolor=ft.Colors.RED_700)
                page.snack_bar.open = True
                
                btn_ingresar.text = "Iniciar Sesión"
                btn_ingresar.disabled = False
                page.update()

        except Exception as ex:
            sock.settimeout(None)
            print(f"Error en Login: {ex}")
            page.snack_bar = ft.SnackBar(ft.Text("Error de red al conectar con el servidor"), bgcolor=ft.Colors.RED_900)
            page.snack_bar.open = True
            
            btn_ingresar.text = "Iniciar Sesión"
            btn_ingresar.disabled = False
            page.update()

    # Asignar el evento al botón
    btn_ingresar.on_click = btn_ingresar_click

    # --- Estructura Visual ---
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