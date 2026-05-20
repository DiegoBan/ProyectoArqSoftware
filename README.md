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

### Base de Datos
Como base de datos utilizamos postgreSQL, ya que gracias a su modelo relacional y estructura permite crear las relaciones necesarias sin problemas a la vez que se mantienen los datos consistentemente, cumpliendo con las propiedades ACID (Atomicidad, Consistencia, Aislamiento y Durabilidad), algo de suma importancia para un software al que no se le puede pasar por alto nada.
<p align="center">
    <img src=".DB/documentacion/entidad_relacion.png" alt="entidad-relacion" />
</p>
<p align="center">
    <img src=".DB/documentacion/modelo_relacional.png" alt="modelo relacional" />
</p>