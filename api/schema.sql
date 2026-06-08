CREATE DATABASE IF NOT EXISTS turismo_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE turismo_db;

CREATE TABLE IF NOT EXISTS ofertas (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(200)    NOT NULL,
    descripcion TEXT,
    precio      DECIMAL(10, 2)  NOT NULL,
    duracion    VARCHAR(100),
    destino     VARCHAR(200),
    imagen_url  VARCHAR(500),
    activo      TINYINT(1)      DEFAULT 1,
    creado_en   TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reservas (
    id                 INT AUTO_INCREMENT PRIMARY KEY,
    nombre             VARCHAR(200)   NOT NULL,
    email              VARCHAR(200)   NOT NULL,
    telefono           VARCHAR(30),
    oferta_id          INT            NOT NULL,
    fecha_reserva      DATE           NOT NULL,
    cantidad_personas  INT            DEFAULT 1,
    comentarios        TEXT,
    estado             VARCHAR(20)    DEFAULT 'pendiente',
    fecha_creacion     TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (oferta_id) REFERENCES ofertas(id)
);

CREATE TABLE IF NOT EXISTS sugerencias (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    nombre           VARCHAR(200)   NOT NULL,
    email            VARCHAR(200),
    mensaje          TEXT           NOT NULL,
    fecha_creacion   TIMESTAMP      DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ofertas (nombre, descripcion, precio, duracion, destino, imagen_url) VALUES
('Punta Cana All-Inclusive',
 'Disfruta del paraiso caribeno con todo incluido en un resort 5 estrellas.',
 45000.00, '5 dias / 4 noches', 'Punta Cana, RD', '/descarga.jpeg'),

('Jarabacoa Aventura',
 'Senderismo, rafting y naturaleza en el corazon de la Cordillera Central.',
 8500.00, '3 dias / 2 noches', 'Jarabacoa, RD', '/descarga1.jpeg'),

('Santo Domingo Colonial',
 'Recorre la Ciudad Colonial, patrimonio de la humanidad, con guia experto.',
 3200.00, '2 dias / 1 noche', 'Santo Domingo, RD', '/descarga2.jpeg');
