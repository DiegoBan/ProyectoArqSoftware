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
),
 (
    '21.189.329-k', 
    'brancoburotto@gmail.com', 
    'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 
    'Branco', 
    'Burotto', 
    'admin', 
    '+56956953291', 
    '2004-02-26'
);

INSERT INTO clientes (nombre, rut_empresa) VALUES
('Tecnologia Global SpA', 761234569),
('Inversiones del Norte Ltda', 772345671),
('Comercializadora Sur SA', 783456782);

INSERT INTO cliente_contacto (id_cliente, nombre, email, telefono) VALUES
(1, 'Pedro Morales', 'pmorales@tecnoglobal.cl', '+56955555555'),
(1, 'Luisa Fernandez', 'lfernandez@tecnoglobal.cl', '+56966666666'),
(2, 'Roberto Gomez', 'rgomez@invnorte.cl', '+56977777777'),
(3, 'Carmen Tapia', 'ctapia@comsur.cl', '+56988888888');

INSERT INTO productos (nombre, familia, subfamilia, descripcion, PN, serie) VALUES
('Notebook Pro 15', 'Computacion', 'Laptops', 'Notebook 15 pulgadas 16GB RAM 512GB SSD', 'NBPRO15', 'S001'),
('Monitor 27 4K', 'Perifericos', 'Monitores', 'Monitor 27 pulgadas resolucion 4K UHD', 'MON27K', 'S002'),
('Teclado Mecanico', 'Perifericos', 'Teclados', 'Teclado mecanico switches red', 'TECMEC01', 'S003'),
('Servidor Rack 1U', 'Infraestructura', 'Servidores', 'Servidor 1U 64GB RAM 2TB NVMe', 'SRVR1UX', 'S004'),
('Switch 24 Puertos PoE', 'Redes', 'Switches', 'Switch administrable 24 puertos Gigabit PoE', 'SW24POE', 'S005');