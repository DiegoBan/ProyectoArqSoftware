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

#### 2. iniciar sesión (`iniciar_sesion`)
Cuando un cliente solicita iniciar sesión en su cuenta previamente registrada, el servicio espera recibir un JSON con la acción y los datos correspondientes.

**JSON recibido desde el Cliente**
```json
{
  "accion": "iniciar_sesion",
  "email": "el7@colocolo.cl",
  "password_hash": "$2b$12$K3B...hash_de_la_contraseña..."
}
```
