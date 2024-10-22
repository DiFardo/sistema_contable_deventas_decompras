CREATE TABLE tipos_usuario (
    id_tipo_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    apellido VARCHAR(255) NOT NULL,
    nombre_usuario VARCHAR(255) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    fecha_nacimiento DATE,
    tipo_usuario_id INT,
    token VARCHAR(255),
    FOREIGN KEY (tipo_usuario_id) REFERENCES tipos_usuario(id_tipo_usuario)
);

CREATE TABLE categorias (
    id_categoria INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_creacion DATE default CURRENT_TIMESTAMP
);

CREATE TABLE productos (
    id_producto INT PRIMARY KEY AUTO_INCREMENT,
    nombre_producto VARCHAR(255) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL,
    id_categoria INT,
    imagen VARCHAR(255),
    talla VARCHAR(50),
    genero VARCHAR(50),
    fecha_creacion date default CURRENT_TIMESTAMP,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
);

CREATE TABLE pedidos (
    id_pedido INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10, 2) NOT NULL,
    estado VARCHAR(50) NOT NULL,
    registrado_en_contable BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE detalles_pedido (
    id_detalle INT PRIMARY KEY AUTO_INCREMENT,
    id_pedido INT,
    id_producto INT,
    cantidad INT NOT NULL,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

CREATE TABLE tarjetas (
    id_tarjeta INT PRIMARY KEY AUTO_INCREMENT,
    numero_tarjeta VARCHAR(20) NOT NULL,
    titular VARCHAR(255) NOT NULL,
    fecha_vencimiento DATE,
    cvv VARCHAR(4),
    id_usuario INT,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE direcciones (
    id_direccion INT PRIMARY KEY AUTO_INCREMENT,
    pais varchar(150) not null,
    departamento varchar(150) not null,
    ciudad varchar(150) not null,
    direccion_1 VARCHAR(255) NOT NULL,
    direccion_2 VARCHAR(255),
    id_usuario INT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE pagos (
    id_pago INT PRIMARY KEY AUTO_INCREMENT,
    id_pedido INT,
    id_tarjeta INT,
    total DECIMAL(10, 2) NOT NULL,
    fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido),
    FOREIGN KEY (id_tarjeta) REFERENCES tarjetas(id_tarjeta)
);

CREATE TABLE comprobante_pago (
    id_comprobante INT PRIMARY KEY AUTO_INCREMENT,
    id_pedido INT NOT NULL,
    tipo_comprobante VARCHAR(50) NOT NULL,
    serie_comprobante VARCHAR(10) NOT NULL,
    numero_comprobante VARCHAR(10) NOT NULL,
    UNIQUE (serie_comprobante, numero_comprobante),
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
);

INSERT INTO `tipos_usuario` (`nombre`) VALUES ('Administrador');

INSERT INTO `tipos_usuario` (`nombre`) VALUES ('Cliente');

CREATE TABLE proveedores (
    id_proveedor INT PRIMARY KEY AUTO_INCREMENT,
    nombre_proveedor VARCHAR(255) NOT NULL,
    direccion VARCHAR(255),
    telefono VARCHAR(20),
    email VARCHAR(255)
);

CREATE TABLE compras (
    id_compra INT PRIMARY KEY AUTO_INCREMENT,
    id_proveedor INT,
    fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10, 2) NOT NULL,
    estado VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
);

CREATE TABLE detalles_compra (
    id_detalle_compra INT PRIMARY KEY AUTO_INCREMENT,
    id_compra INT,
    id_producto INT,
    cantidad INT NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_compra) REFERENCES compras(id_compra),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

CREATE TABLE insumos_materiales (
    id_insumo INT PRIMARY KEY AUTO_INCREMENT,
    nombre_insumo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_proveedor INT,
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
);

INSERT INTO proveedores (nombre_proveedor, telefono, email, direccion) VALUES ('Maderas del Norte S.A.', '923456123', 'contacto@maderasdelnorte.com', 'Carretera Central Km. 12, Lima');
INSERT INTO proveedores (nombre_proveedor, telefono, email, direccion) VALUES ('Decoraciones Elegantes', '911223344', 'ventas@decoelegantes.com', 'Av. Las Palmeras 321, Piura');
INSERT INTO proveedores (nombre_proveedor, telefono, email, direccion) VALUES ('Fabricantes de Tapices Modernos', '944556677', 'contacto@tapicesmodernos.com', 'Jr. Los Álamos 890, Huancayo');
INSERT INTO proveedores (nombre_proveedor, telefono, email, direccion) VALUES ('Materiales Premium para Muebles', '999887766', 'info@materialespremium.com', 'Av. Industrial 1000, Lima');
INSERT INTO proveedores (nombre_proveedor, telefono, email, direccion) VALUES ('Diseños y Acabados de Lujo', '922334455', 'ventas@disenoslujo.com', 'Calle Arte Moderno 222, Arequipa');

INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Planchas de Madera de Roble', 'Planchas de madera de roble de alta calidad para muebles', 50.00, 100, 1);
INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Planchas de Madera de Pino', 'Planchas de madera de pino estándar', 30.00, 200, 1);
INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Láminas de Chapa de Nogal', 'Chapa de nogal para acabados de lujo', 15.00, 150, 2);
INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Material de Tapicería de Cuero', 'Cuero genuino para tapicería', 100.00, 50, 3);
INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Tela de Algodón', 'Tela de algodón para tapicería', 20.00, 300, 3);
INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Espuma para Relleno', 'Espuma de alta densidad para cojines', 25.00, 80, 3);
INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Tornillos de Acero', 'Tornillos de acero inoxidable tamaño estándar', 0.10, 1000, 4);
INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Bisagras de Latón', 'Bisagras de latón para puertas de armario', 2.50, 500, 4);
INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Paneles de Vidrio', 'Paneles de vidrio templado para vitrinas', 40.00, 70, 5);
INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Paquetes de Lija', 'Paquetes de lija grano fino para acabado', 5.00, 200, 4);
INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Tinte para Madera', 'Tinte color caoba para madera', 15.00, 120, 2);
INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Barniz', 'Barniz transparente para protección de madera', 18.00, 150, 2);
INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Pegamento para Madera', 'Pegamento de secado rápido para madera', 7.00, 300, 4);
INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Clavos', 'Clavos de acero de diferentes tamaños', 0.05, 2000, 4);
INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Correderas para Cajones', 'Correderas metálicas para cajones', 12.00, 100, 5);
INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Manijas para Muebles', 'Manijas de acero inoxidable para muebles', 3.50, 400, 5);
INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Tableros MDF', 'Tableros de fibra de densidad media', 25.00, 150, 1);
INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Hojas de Contrachapado', 'Hojas de madera contrachapada', 20.00, 180, 1);
INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Hilo para Tapicería', 'Hilo resistente para trabajos de tapicería', 8.00, 250, 3);
INSERT INTO insumos_materiales (nombre_insumo, descripcion, precio_unitario, stock, id_proveedor) VALUES ('Relleno para Cojines', 'Relleno de fibra sintética para cojines', 10.00, 200, 3);