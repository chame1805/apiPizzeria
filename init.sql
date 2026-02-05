-- 1. Crear tabla de Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    direccion TEXT NOT NULL
);

-- 2. Crear tabla de Productos (Menú de Pizzas)
-- Usamos DECIMAL(10,2) para manejar dinero con precisión (evita errores de decimales)
CREATE TABLE IF NOT EXISTS productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    precio DECIMAL(10, 2) NOT NULL
);

-- 3. Crear tabla de Órdenes (Cabecera del ticket)
CREATE TABLE IF NOT EXISTS ordenes (
    id SERIAL PRIMARY KEY,
    cliente_id INT REFERENCES clientes(id) ON DELETE SET NULL, -- Si borras cliente, la venta queda (histórico)
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Guarda fecha y hora automática
    total_venta DECIMAL(10, 2) NOT NULL,
    pago_cliente DECIMAL(10, 2) NOT NULL,
    cambio DECIMAL(10, 2) NOT NULL,
    estatus VARCHAR(20) DEFAULT 'PAGADA' -- Valores: 'PAGADA', 'CANCELADA'
);

-- 4. Crear tabla de Detalle de Orden (Qué pizzas lleva cada orden)
CREATE TABLE IF NOT EXISTS detalles_orden (
    id SERIAL PRIMARY KEY,
    orden_id INT REFERENCES ordenes(id) ON DELETE CASCADE, -- Si borras orden, se borran sus detalles
    producto_id INT REFERENCES productos(id),
    cantidad INT NOT NULL DEFAULT 1,
    subtotal DECIMAL(10, 2) NOT NULL -- (precio * cantidad) guardado por si cambia el precio futuro
);

-- ==========================================
-- DATOS INICIALES (SEED)
-- ==========================================

-- Insertar el menú de pizzas con tus precios definidos
INSERT INTO productos (nombre, precio) VALUES 
    ('Pepperoni', 139.00),
    ('Hawaiana', 159.00),
    ('Carnes Frías', 189.00),
    ('Mexicana', 189.00),
    ('3 Quesos', 189.00),
    ('Europea', 189.00)
ON CONFLICT (nombre) DO NOTHING; -- Evita error si reinicias el contenedor y ya existen