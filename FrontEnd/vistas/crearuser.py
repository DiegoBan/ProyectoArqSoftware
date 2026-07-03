import flet as ft
import json
import hashlib
from datetime import date
from soa_lib import send_message

# ── Helpers ──────────────────────────────────────────────────────────────────
PREFIJO_TELEFONO = "+569"

def _email_valido(email: str) -> bool:
    """Validación mínima: contiene '@' y un '.' después del arroba."""
    partes = email.split("@")
    if len(partes) != 2:
        return False
    dominio = partes[1]
    return "." in dominio and len(dominio.split(".")[-1]) >= 2


def _rut_valido(rut: str) -> bool:
    """Valida RUT chileno calculando el dígito verificador."""
    rut = rut.strip().upper().replace(".", "").replace("-", "")
    if len(rut) < 2:
        return False
    cuerpo, dv = rut[:-1], rut[-1]
    if not cuerpo.isdigit():
        return False
    suma, factor = 0, 2
    for d in reversed(cuerpo):
        suma += int(d) * factor
        factor = factor + 1 if factor < 7 else 2
    esperado = 11 - (suma % 11)
    if esperado == 11:
        esperado = "0"
    elif esperado == 10:
        esperado = "K"
    else:
        esperado = str(esperado)
    return dv == esperado


def _formatear_rut(raw: str) -> str:
    """Formatea el texto ingresado como XX.XXX.XXX-X mientras el usuario escribe."""
    # Conservar solo dígitos y K
    limpio = "".join(c for c in raw.upper() if c.isdigit() or c == "K")
    if len(limpio) <= 1:
        return limpio
    cuerpo, dv = limpio[:-1], limpio[-1]
    # Agregar puntos cada 3 dígitos desde la derecha
    cuerpo_fmt = ""
    for i, c in enumerate(reversed(cuerpo)):
        if i > 0 and i % 3 == 0:
            cuerpo_fmt = "." + cuerpo_fmt
        cuerpo_fmt = c + cuerpo_fmt
    return f"{cuerpo_fmt}-{dv}"


def _dias_en_mes(mes: int, anio: int) -> int:
    """Retorna la cantidad de días según mes y año (respeta bisiestos)."""
    import calendar
    return calendar.monthrange(anio, mes)[1]

# ── Vista ─────────────────────────────────────────────────────────────────────
def vista_crear_usuario(page: ft.Page, sock, cambiar_vista_func):

    # --- Definición de Campos de Texto ---
    # ── RUT con formato automático y validación en tiempo real ─────────────────
    txt_rut = ft.TextField(
        label="RUT (ej: 12.345.678-9)",
        width=350,
        max_length=12,
        hint_text="12.345.678-9",
        input_filter=ft.InputFilter(allow=True, regex_string=r"[\d\.\-kK]"),
    )

    def validar_rut(e):
        raw = txt_rut.value or ""
        formateado = _formatear_rut(raw)
        if formateado != raw:
            txt_rut.value = formateado
        valor = txt_rut.value.strip()
        if valor == "" or len(valor.replace(".", "").replace("-", "")) < 2:
            txt_rut.error_text = None
            txt_rut.suffix_icon = None
        elif _rut_valido(valor):
            txt_rut.error_text = None
            txt_rut.suffix_icon = ft.Icons.CHECK_CIRCLE
            txt_rut.suffix_style = ft.TextStyle(color=ft.Colors.GREEN_400)
        else:
            txt_rut.error_text = "RUT inválido"
            txt_rut.suffix_icon = ft.Icons.ERROR
        page.update()

    txt_rut.on_change = validar_rut
    txt_email = ft.TextField(label="Email", width=350)
    txt_password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=350)
    txt_nombre = ft.TextField(label="Nombre", width=350)
    txt_apellido = ft.TextField(label="Apellido", width=350)
    txt_password = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        width=350
    )

    dropdown_rol = ft.Dropdown(
        label="Rol del Trabajador",
        width=350,
        options=[
            ft.dropdown.Option("admin"),
            ft.dropdown.Option("vendedor"),
            ft.dropdown.Option("contador"),
        ],
        value="vendedor"
    )

    # ── Email con validación en tiempo real ──────────────────────────────────
    txt_email = ft.TextField(
        label="Email",
        width=350,
        keyboard_type=ft.KeyboardType.EMAIL,
        hint_text="ejemplo@gmail.com",
        capitalization=ft.TextCapitalization.NONE,
    )

    def validar_email(e):
        valor = txt_email.value.strip()
        if valor == "":
            txt_email.error_text = None
            txt_email.suffix_icon = None
        elif _email_valido(valor):
            txt_email.error_text = None
            txt_email.suffix_icon = ft.Icons.CHECK_CIRCLE
            txt_email.suffix_style = ft.TextStyle(color=ft.Colors.GREEN_400)
        else:
            txt_email.error_text = "Formato inválido  (ej: nombre@dominio.com)"
            txt_email.suffix_icon = ft.Icons.ERROR
        page.update()

    txt_email.on_change = validar_email

    # ── Teléfono con prefijo +569 automático ─────────────────────────────────
    txt_telefono = ft.TextField(
        label="Teléfono",
        width=350,
        value=PREFIJO_TELEFONO,
        max_length=12,           # +569 (4) + 8 dígitos = 12
        hint_text="+56912345678",
        keyboard_type=ft.KeyboardType.PHONE,
        input_filter=ft.InputFilter(allow=True, regex_string=r"[\+\d]"),
    )

    def proteger_prefijo(e):
        """Evita que el usuario borre el +569 y asegura que solo haya números después."""
        val = txt_telefono.value or ""
        
        if val.startswith(PREFIJO_TELEFONO):
            resto = val[len(PREFIJO_TELEFONO):]
        else:
            # Si el usuario intentó borrar parte del prefijo, extraemos todos los números
            digitos = "".join(c for c in val if c.isdigit())
            if digitos.startswith("569"):
                resto = digitos[3:]
            elif digitos.startswith("56"):
                resto = digitos[2:]
            elif digitos.startswith("5"):
                resto = digitos[1:]
            else:
                resto = digitos

        # El resto del teléfono debe ser estrictamente numérico (máximo 8 dígitos)
        resto_numerico = "".join(c for c in resto if c.isdigit())[:8]
        
        nuevo_valor = PREFIJO_TELEFONO + resto_numerico
        if txt_telefono.value != nuevo_valor:
            txt_telefono.value = nuevo_valor
            page.update()

    txt_telefono.on_change = proteger_prefijo

    # ── Fecha de nacimiento con 3 dropdowns ──────────────────────────────────
    anio_actual = date.today().year

    anios = [ft.dropdown.Option(str(a)) for a in range(anio_actual - 80, anio_actual - 17)]
    meses = [
        ft.dropdown.Option(str(m).zfill(2), text=nombre)
        for m, nombre in enumerate(
            ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
             "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"], 1
        )
    ]
    dias_opciones = [ft.dropdown.Option(str(d).zfill(2)) for d in range(1, 32)]

    dd_anio = ft.Dropdown(label="Año", options=anios)
    dd_mes  = ft.Dropdown(label="Mes", options=meses)
    dd_dia  = ft.Dropdown(label="Día", options=dias_opciones)

    def actualizar_dias(e=None):
        """Ajusta los días disponibles según mes y año seleccionados."""
        mes_val  = int(dd_mes.value)  if dd_mes.value  else None
        anio_val = int(dd_anio.value) if dd_anio.value else None
        if mes_val and anio_val:
            max_dias = _dias_en_mes(mes_val, anio_val)
            dd_dia.options = [ft.dropdown.Option(str(d).zfill(2)) for d in range(1, max_dias + 1)]
            # Si el día actual supera el máximo, lo reseteamos
            if dd_dia.value and int(dd_dia.value) > max_dias:
                dd_dia.value = None
            page.update()

    dd_mes.on_change  = actualizar_dias
    dd_anio.on_change = actualizar_dias

    lbl_fecha = ft.Text("Fecha de Nacimiento", size=13, color=ft.Colors.GREY_400)
    row_fecha = ft.Row([dd_dia, dd_mes, dd_anio], spacing=6, tight=True)

    # ── Lógica de envío ──────────────────────────────────────────────────────
    def btn_crear_click(e):
        email = txt_email.value.strip()

        # Validaciones
        if not txt_rut.value or not email:
            page.overlay.append(ft.SnackBar(
                ft.Text("RUT y Email son obligatorios"), bgcolor=ft.Colors.ORANGE_700))
            page.overlay[-1].open = True
            page.update()
            return

        if not _rut_valido(txt_rut.value):
            page.overlay.append(ft.SnackBar(
                ft.Text("El RUT ingresado no es válido"), bgcolor=ft.Colors.RED_700))
            page.overlay[-1].open = True
            page.update()
            return

        if not _email_valido(email):
            page.overlay.append(ft.SnackBar(
                ft.Text("El email no tiene un formato válido"), bgcolor=ft.Colors.RED_700))
            page.overlay[-1].open = True
            page.update()
            return

        telefono_val = txt_telefono.value or ""
        if len(telefono_val) < 12:
            page.overlay.append(ft.SnackBar(
                ft.Text("El teléfono debe tener 8 dígitos luego del +569"), bgcolor=ft.Colors.ORANGE_700))
            page.overlay[-1].open = True
            page.update()
            return

        if not dd_dia.value or not dd_mes.value or not dd_anio.value:
            page.overlay.append(ft.SnackBar(
                ft.Text("Seleccione la fecha de nacimiento completa"), bgcolor=ft.Colors.ORANGE_700))
            page.overlay[-1].open = True
            page.update()
            return

        fecha_nac = f"{dd_anio.value}-{dd_mes.value}-{dd_dia.value}"
        password_hash = hashlib.sha256(txt_password.value.encode("utf-8")).hexdigest()

        payload = {
            "accion": "crear_usuario",
            "user_rut": page.session.store.get("rut"),
            "rut": txt_rut.value,
            "email": email,
            "password_hash": password_hash,
            "nombre": txt_nombre.value,
            "apellido": txt_apellido.value,
            "rol": dropdown_rol.value,
            "telefono": telefono_val,
            "Fecha_nacimiento": fecha_nac
        }

        send_message(sock, "usuar", json.dumps(payload))

        # Limpiar formulario
        txt_rut.value = ""
        txt_email.value = ""
        txt_email.error_text = None
        txt_email.suffix_icon = None
        txt_password.value = ""
        txt_nombre.value = ""
        txt_apellido.value = ""
        txt_telefono.value = PREFIJO_TELEFONO
        dd_dia.value = None
        dd_mes.value = None
        dd_anio.value = None
        page.update()

    # ── Botones ──────────────────────────────────────────────────────────────
    btn_guardar = ft.ElevatedButton(
        "Crear Usuario",
        on_click=btn_crear_click,
        width=350, height=45,
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE
    )
    btn_volver = ft.TextButton(
        "← Volver al Dashboard",
        on_click=lambda _: cambiar_vista_func("dashboard")
    )

    # ── Estructura visual ─────────────────────────────────────────────────────
    formulario = ft.Column(
        controls=[
            ft.Text("Registro de Nuevo Usuario", size=26, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            txt_rut,
            txt_email,
            txt_password,
            txt_nombre,
            txt_apellido,
            dropdown_rol,
            txt_telefono,
            ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
            lbl_fecha,
            row_fecha,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            btn_guardar,
            btn_volver,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO,
    )

    return ft.Container(
        content=formulario,
        alignment=ft.Alignment.CENTER,
        expand=True,
        padding=20
    )