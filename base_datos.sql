-- ============================================================
-- BASE DE DATOS: PULPERÍA L&M
-- Instrucciones: Abrir DB Browser for SQLite -> New Database
-- -> guardar como "db" -> pestaña "Execute SQL" -> pegar este
-- script -> clic en Execute -> Write Changes
-- ============================================================

-- Tabla de productos
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    precio REAL NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0
);

-- Tabla de ventas (encabezado de factura)
CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    cliente TEXT NOT NULL,
    total REAL NOT NULL
);

-- Tabla de detalle de venta (líneas de cada factura)
CREATE TABLE IF NOT EXISTS detalle_venta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id INTEGER NOT NULL,
    producto TEXT NOT NULL,
    cantidad INTEGER NOT NULL,
    precio REAL NOT NULL,
    subtotal REAL NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES ventas(id)
);

-- Datos de ejemplo: productos de la pulpería
INSERT INTO productos (nombre, precio, stock) VALUES
    ('Coca Cola 600ml', 18.00, 24),
    ('Pan de barra', 25.00, 15),
    ('Huevos (unidad)', 4.50, 120),
    ('Arroz 1lb', 14.00, 30),
    ('Frijoles 1lb', 16.00, 25),
    ('Aceite 500ml', 42.00, 10),
    ('Azúcar 1lb', 13.00, 20),
    ('Galleta paquete', 8.00, 40);

-- Datos de ejemplo: ventas de prueba
INSERT INTO ventas (fecha, cliente, total) VALUES
    ('2026-09-21 09:15:32', 'María Rodríguez', 68.50),
    ('2026-09-21 11:42:10', 'Cliente general', 56.00);

-- Detalle de la venta 1
INSERT INTO detalle_venta (venta_id, producto, cantidad, precio, subtotal) VALUES
    (1, 'Coca Cola 600ml', 2, 18.00, 36.00),
    (1, 'Pan de barra', 1, 25.00, 25.00),
    (1, 'Huevos (unidad)', 4, 4.50, 18.00);

-- Detalle de la venta 2
INSERT INTO detalle_venta (venta_id, producto, cantidad, precio, subtotal) VALUES
    (2, 'Arroz 1lb', 2, 14.00, 28.00),
    (2, 'Frijoles 1lb', 1, 16.00, 16.00),
    (2, 'Galleta paquete', 2, 8.00, 16.00);
