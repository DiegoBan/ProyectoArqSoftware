# Proyecto Arquitectura de Software: 
Repositorio para nuestro proyecto de Arquitectura de Software.

### Integrantes
- Diego Banda ([DiegoBan](https://github.com/DiegoBan))
- Branco Burotto ([branxeto](https://github.com/branxeto))
- Valentína Garcia ([balentula](https://github.com/balentula))
- Diego Salazar ([HoHenHeimpepsi](https://github.com/HoHenHeimpepsi))

## Sobre el proyecto
Software creado con el objetivo de eficientizar, y coordinar registro de ventas, facturación, clientes, etc. Se utiliza la arquitectura SOA, con un bus central que gestiona la comunicación entre el cliente de la aplicación y los distintos servicios encargados de la lógica, cálculos, guardado de registros en base de datos, etc.

### Cómo levantar proyecto
Los distintos servicios están creados para ser contenidos en Docker, cada uno con su propio contenedor, de esta manera se mantiene el ambiente correctamente separado para cada uno.

Para levantar el proyecto se utiliza el siguiente comando en la carpeta principal del proyecto:
```
docker compose up --build -d
```

## Cliente

### Librerias FrontEnd
usar el comando 
```
pip install -r requirements.txt
```
Luego para iniciar el front se debe ejecutar en la carpeta "FrontEnd" el siguiente comando.
```
python main.py
```
De esa forma se usa ejecutaran las vistas de la aplicación 

## Servicios

### Base de Datos
Como base de datos utilizamos postgreSQL, ya que gracias a su modelo relacional y estructura permite crear las relaciones necesarias sin problemas a la vez que se mantienen los datos consistentemente, cumpliendo con las propiedades ACID (Atomicidad, Consistencia, Aislamiento y Durabilidad), algo de suma importancia para un software al que no se le puede pasar por alto nada.

<p align="center">
    <img src="./DB/documentacion/entidad_relacion.png" alt="entidad-relacion" />
</p>
<p align="center">
    <img src="./DB/documentacion/modelo_relacional.png" alt="modelo relacional" />
</p>

En caso de querer acceder a la consola del contenedor con postgreSQL, ejecuta:
```
docker exec -it postgres_db psql -U admin -d db
```

La librería utilizada para conectar PostgresSQL con Python será 'psycopg2'.

### Servicio Usuario
El servicio **Usuario** tiene la responsabilidad de gestionar las operaciones lógicas sobre la tabla `Usuarios` en la base de datos. Actúa como intermediario: recibe la petición del servicio *Cliente*, valida la información de negocio y construye la consulta SQL para enviarla al servicio *Base de Datos* a través del bus.

**Librerías utilizadas:**
* `time`: Para manejo de pausas o marcas de tiempo.
* `json`: Para la serialización y deserialización de mensajes.
* `soa_lib`: Para la comunicación por sockets con el Bus SOA.

### Tareas del Servicio

#### 1. Crear usuario (`crear_usuario`)
Cuando un cliente solicita registrar un nuevo usuario, el servicio espera recibir un JSON con la acción y los datos correspondientes.

**JSON recibido desde el Cliente:**
```json
{
  "accion": "crear_usuario",
  "rut": "12.345.678-9",
  "email": "el7@colocolo.cl",
  "password_hash": "$2b$12$K3B...hash_de_la_contraseña...",
  "nombre": "Esteban",
  "apellido": "Paredes",
  "rol": "usuario",
  "telefono": "+56961486932",
  "Fecha_nacimiento": "1980-08-01"
}
```

#### 2. Iniciar sesión (`iniciar_sesion`)
Cuando un cliente solicita iniciar sesión en su cuenta previamente registrada, el servicio espera recibir un JSON con la acción y los datos correspondientes.

**JSON recibido desde el Cliente**
```json
{
  "accion": "iniciar_sesion",
  "email": "el7@colocolo.cl",
  "password_hash": "$2b$12$K3B...hash_de_la_contraseña..."
}
```

#### 3. Modificar rol (`modificar_rol`)
Cuando un administrador desea cambiar el rol de un usuario del sistema, primero debe encontrarse debidamente logeado con anterioridad y tener un rol apto para realizar tal cambio. La función espera recibir un JSON de la siguiente manera.

**JSON recibido desde el Cliente**
```json
{
  "accion": "modificar_rol",
  "modificador_id": "3",
  "modificar_id": "7",
  "nuevo_rol": "vendedor"
}
```

El cliente recibirá un json según el resultado de la operación:

- Usuario de modificador no encontrado:
```json
{
  "estado": "error",
  "mensaje": "Usuario modificador no encontrado"
}
```
- Modificador no es admin:
```json
{
  "estado": "error",
  "mensaje": "Usuario no es admin"
}
```
- Error interno:
```json
{
  "estado": "error",
  "mensaje": "error interno del servidor"
}
```
- Usuario a modificar no existe
```json
{
  "estado": "error",
  "mensaje": "Usuario a modificar no existe"
}
```
- Modificación con éxito
```json
{
  "estado": "ok",
  "mensaje": "rol modificado"
}
```
---
### Servicio Cliente

El servicio Cliente es el encargado de gestionar la información de las entidades a las que se les factura o se les registra una venta. Al igual que los demás servicios, recibe peticiones desde el bus SOA, valida permisos críticos (como verificar si el usuario es administrador) y formatea los registros de la base de datos para entregarlos limpios al FrontEnd.

### Tareas del Servicio
#### 1. Obtener clientes (obtener_clientes)

Cuando una vista del FrontEnd requiere listar el directorio de clientes, el servicio realiza una consulta a la base de datos y transforma los registros crudos en una lista de diccionarios, facilitando su consumo y renderizado.

Respuesta JSON enviada hacia el Cliente (Ejemplo exitoso):
JSON
```json
{
  "estado": "ok",
  "mensaje": "Clientes obtenidos",
  "clientes": [
    {
      "id": 1,
      "nombre": "Blanco y Negro S.A.",
      "rut_empresa": "99.999.999-9"
    },
    {
      "id": 2,
      "nombre": "Inmobiliaria Monumental",
      "rut_empresa": "88.888.888-8"
    }
  ]
}
```
#### 2. Actualizar cliente (actualizar_cliente)

Este método se encarga de modificar los datos de un cliente existente. Cuenta con una validación de seguridad estricta: antes de ejecutar el UPDATE, verifica en la tabla de usuarios que quien solicita la acción posea el rol de admin.

JSON esperado desde el Cliente:
JSON
```json
{
  "accion": "actualizar_cliente",
  "user": "12.345.678-9",
  "id": 1,
  "nombre": "Nuevo Nombre Cliente",
  "rut_empresa": "77.777.777-7"
}
```
Respuesta JSON enviada hacia el Cliente (Ejemplo exitoso):
JSON
``` json
{
  "estado": "ok",
  "mensaje": "Actualización exitosa",
  "detalles": {
    "nombre": "Nuevo Nombre Cliente",
    "rut_empresa": "77.777.777-7"
  }
}
```
