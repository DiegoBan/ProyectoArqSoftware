INSERT INTO usuarios (rut, email, password_hash, nombre, apellido, rol, telefono, Fecha_nacimiento) 
VALUES (
    '11.111.111-1', 
    'admin@erp.cl', 
    'e998a9508298a0116456277517f01a03886bd8a0de2e394946be1caaf7cb2752', 
    'Super', 
    'Admin', 
    'admin', 
    '+56900000000', 
    '1990-01-01'
);
INSERT INTO clientes (nombre, rut_empresa) 
VALUES ('Blanco y Negro S.A.', 99999999);