# Pizzería API — Documentación de Endpoints

> **Base URL:** `http://localhost:8000`  
> **Swagger UI:** `http://localhost:8000/docs`  
> **Versión:** 2.0.0

---

## Índice

1. [Autenticación](#1-autenticación)
2. [Productos](#2-productos)
3. [Órdenes (cocina/mesero)](#3-órdenes-cocinamensero)
4. [Perfil del mesero](#4-perfil-del-mesero)
5. [Ventas (historial)](#5-ventas--historial)
6. [WebSockets](#6-websockets)
7. [Roles y permisos](#7-roles-y-permisos)

---

## 1. Autenticación

### `POST /auth/register`
Registra un nuevo usuario en el sistema. No requiere token.

**Body (JSON):**
```json
{
  "email":    "usuario@ejemplo.com",
  "name":     "Nombre Completo",
  "password": "contraseña123",
  "rol":      "MESERO"
}
```

| Campo      | Tipo   | Requerido | Valores válidos             |
|------------|--------|-----------|-----------------------------|
| `email`    | string | ✅        | Email válido, único         |
| `name`     | string | ✅        | Texto libre                 |
| `password` | string | ✅        | Texto libre                 |
| `rol`      | string | ❌        | `MESERO`, `COCINERO`, `ADMIN` (default: `MESERO`) |

**Respuesta `201`:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "usuario": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "nombre": "Nombre Completo",
    "rol": "MESERO",
    "fecha_registro": "2026-03-10T20:00:00"
  }
}
```

---

### `POST /auth/login`
Inicia sesión y obtiene el token JWT.

**Body (JSON):**
```json
{
  "email":    "usuario@ejemplo.com",
  "password": "contraseña123"
}
```

| Campo      | Tipo   | Requerido |
|------------|--------|-----------|
| `email`    | string | ✅        |
| `password` | string | ✅        |

**Respuesta `200`:** (mismo formato que `/auth/register`)

**Error `401`:** Credenciales incorrectas.

---

## 2. Productos

### `GET /menu`
Devuelve la lista completa de productos. **Sin autenticación.**

**Respuesta `200`:**
```json
[
  { "id": 1, "nombre": "Pepperoni", "precio": 139.0 },
  { "id": 2, "nombre": "Hawaiana",  "precio": 159.0 }
]
```

---

### `GET /productos/`
Igual que `/menu`. **Sin autenticación.**

---

### `GET /productos/{producto_id}`
Devuelve un producto por su ID. **Sin autenticación.**

**Parámetro de ruta:** `producto_id` (int)

**Respuesta `200`:**
```json
{ "id": 1, "nombre": "Pepperoni", "precio": 139.0 }
```

---

### `POST /productos/` 🔒 ADMIN
Crea un nuevo producto.

**Headers:** `Authorization: Bearer <token>`

**Body (JSON):**
```json
{
  "nombre": "Pizza Nueva",
  "precio": 199.0
}
```

| Campo    | Tipo   | Requerido | Restricciones          |
|----------|--------|-----------|------------------------|
| `nombre` | string | ✅        | 1–100 caracteres       |
| `precio` | float  | ✅        | Mayor a 0              |

**Respuesta `201`:**
```json
{ "id": 7, "nombre": "Pizza Nueva", "precio": 199.0 }
```

---

### `PUT /productos/{producto_id}` 🔒 ADMIN
Actualiza un producto existente.

**Headers:** `Authorization: Bearer <token>`

**Body (JSON):** Todos los campos son opcionales.
```json
{
  "nombre": "Nuevo Nombre",
  "precio": 220.0
}
```

**Respuesta `200`:** Producto actualizado.

---

### `DELETE /productos/{producto_id}` 🔒 ADMIN
Elimina un producto.

**Headers:** `Authorization: Bearer <token>`

**Respuesta `200`:** Confirmación de eliminación.

---

## 3. Órdenes (cocina/mesero)

### `POST /orders/` 🔒 Token requerido
El mesero crea una nueva orden. El estado inicial siempre es `PENDING`. Hace broadcast WebSocket a la cocina automáticamente.

**Headers:** `Authorization: Bearer <token>`

**Body (JSON):**
```json
{
  "pizza_name":      "Pepperoni",
  "price":           139.0,
  "client_name":     "Juan Pérez",
  "total_paid":      200.0,
  "change_returned": 61.0,
  "table_number":    5,
  "waiter_id":       2
}
```

| Campo             | Tipo   | Requerido | Descripción                          |
|-------------------|--------|-----------|--------------------------------------|
| `pizza_name`      | string | ✅        | Nombre de la pizza                   |
| `price`           | float  | ✅        | Precio de la pizza                   |
| `client_name`     | string | ✅        | Nombre del cliente                   |
| `total_paid`      | float  | ✅        | Dinero que entregó el cliente        |
| `change_returned` | float  | ✅        | Cambio devuelto                      |
| `table_number`    | int    | ✅        | Número de mesa                       |
| `waiter_id`       | int    | ✅        | ID del mesero que toma la orden      |
| `status`          | string | ❌        | Default: `PENDING`                   |

**Respuesta `201`:**
```json
{
  "id": 1,
  "pizza_name": "Pepperoni",
  "price": 139.0,
  "client_name": "Juan Pérez",
  "total_paid": 200.0,
  "change_returned": 61.0,
  "waiter_id": 2,
  "table_number": 5,
  "status": "PENDING",
  "created_at": "2026-03-10T20:00:00",
  "updated_at": "2026-03-10T20:00:00"
}
```

---

### `GET /orders/` 🔒 Token requerido
Devuelve las órdenes activas (`PENDING` e `IN_PROGRESS`) para la pantalla de cocina.

**Headers:** `Authorization: Bearer <token>`

**Respuesta `200`:**
```json
[
  {
    "id": 1,
    "pizza_name": "Pepperoni",
    "table_number": 5,
    "client_name": "Juan Pérez",
    "status": "PENDING",
    "created_at": "2026-03-10T20:00:00"
  }
]
```

---

### `PATCH /orders/{order_id}/status/` 🔒 Token requerido
La cocina cambia el estado de una orden. Flujo: `PENDING → IN_PROGRESS → COMPLETED`.
Al llegar a `COMPLETED`, notifica al mesero por WebSocket automáticamente.

**Headers:** `Authorization: Bearer <token>`

**Parámetro de ruta:** `order_id` (int)

**Body (JSON):**
```json
{
  "status": "IN_PROGRESS"
}
```

| Valor         | Descripción              |
|---------------|--------------------------|
| `PENDING`     | En espera                |
| `IN_PROGRESS` | En preparación (cocina)  |
| `COMPLETED`   | Lista para entregar      |

**Respuesta `200`:**
```json
{
  "id": 1,
  "status": "IN_PROGRESS",
  "updated_at": "2026-03-10T20:05:00"
}
```

---

### `GET /orders/{waiter_id}/completed/` 🔒 Token requerido
Devuelve todas las órdenes `COMPLETED` de un mesero. Útil como historial o fallback si el WebSocket se desconecta.

**Headers:** `Authorization: Bearer <token>`

**Parámetro de ruta:** `waiter_id` (int)

**Respuesta `200`:**
```json
[
  {
    "id": 1,
    "pizza_name": "Pepperoni",
    "table_number": 5,
    "status": "COMPLETED",
    "updated_at": "2026-03-10T20:10:00"
  }
]
```

---

## 4. Perfil del mesero

### `GET /waiters/{user_id}/profile/` 🔒 Token requerido
Obtiene el perfil completo del mesero.

**Headers:** `Authorization: Bearer <token>`

**Respuesta `200`:**
```json
{
  "id": 2,
  "name": "Mesero Test",
  "phone": "0987654321",
  "email": "mesero@pizza.com",
  "photo_url": "http://localhost:8000/static/photos/foto.jpg"
}
```

---

### `PATCH /waiters/{user_id}/profile/` 🔒 Token requerido
Actualiza el nombre y/o teléfono del mesero. Ambos campos son opcionales.

**Headers:** `Authorization: Bearer <token>`

**Body (JSON):**
```json
{
  "name":  "Nuevo Nombre",
  "phone": "0987654321"
}
```

| Campo   | Tipo   | Requerido |
|---------|--------|-----------|
| `name`  | string | ❌        |
| `phone` | string | ❌        |

**Respuesta `200`:** Perfil actualizado (mismo formato que GET).

---

### `POST /waiters/{user_id}/photo/` 🔒 Token requerido
Sube una foto de perfil. Máximo 5 MB.

**Headers:** `Authorization: Bearer <token>`  
**Content-Type:** `multipart/form-data`

**Campo del formulario:** `photo` (archivo de imagen JPEG)

```bash
curl -X POST http://localhost:8000/waiters/2/photo/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "photo=@/ruta/a/foto.jpg"
```

**Respuesta `201`:**
```json
{
  "photo_url": "http://localhost:8000/static/photos/2_foto.jpg"
}
```

---

## 5. Ventas / Historial

### `POST /ordenes/vender`
Registra una nueva venta. **Sin autenticación.**

**Body (JSON):**
```json
{
  "cliente": {
    "nombre":    "Juan Pérez",
    "telefono":  "5551234567",
    "direccion": "Calle Falsa 123"
  },
  "items": [
    { "producto_id": 1, "cantidad": 2 },
    { "producto_id": 3, "cantidad": 1 }
  ],
  "pago_cliente": 1000.0
}
```

**Respuesta `200`:**
```json
{
  "folio":   1,
  "cliente": "Juan Pérez",
  "fecha":   "2026-03-10T20:00:00",
  "total":   467.0,
  "pago":    1000.0,
  "cambio":  533.0,
  "mensaje": "Venta registrada exitosamente"
}
```

---

### `GET /ordenes/historial`
Devuelve el historial completo de todas las ventas. **Sin autenticación.**

**Respuesta `200`:**
```json
[
  {
    "id": 1,
    "cliente_nombre": "Juan Pérez",
    "fecha": "2026-03-10T21:00:00",
    "total_venta": 278.0,
    "pago_cliente": 1000.0,
    "cambio": 722.0,
    "estatus": "PAGADA",
    "detalles": [
      {
        "producto_id": 1,
        "producto_nombre": "Pepperoni",
        "cantidad": 2,
        "precio_unitario": 139.0,
        "subtotal": 278.0
      }
    ]
  }
]
```

---

### `GET /ordenes/{orden_id}`
Obtiene una venta específica por su ID. **Sin autenticación.**

**Respuesta `200`:** Mismo formato que un item del historial.

---

### `DELETE /ordenes/{orden_id}`
Elimina una venta del historial. **Sin autenticación.**

**Respuesta `200`:** Confirmación de eliminación.

---

## 6. WebSockets

Los WebSockets requieren pasar el token JWT como query parameter: `?token=<jwt>`

### `WS /orders/ws/kitchen`
Pantalla de cocina. Recibe eventos en tiempo real cuando:
- Llega una orden nueva → evento `NEW_ORDER`
- Una orden cambia de estado → evento `ORDER_STATUS_CHANGED`

```
ws://localhost:8000/orders/ws/kitchen?token=eyJhbGc...
```

**Evento `NEW_ORDER`:**
```json
{
  "event":        "NEW_ORDER",
  "id":           1,
  "pizza_name":   "Pepperoni",
  "table_number": 5,
  "client_name":  "Juan Pérez",
  "status":       "PENDING",
  "created_at":   "2026-03-10T20:00:00"
}
```

**Evento `ORDER_STATUS_CHANGED`:**
```json
{
  "event":      "ORDER_STATUS_CHANGED",
  "id":         1,
  "status":     "IN_PROGRESS",
  "updated_at": "2026-03-10T20:05:00"
}
```

---

### `WS /orders/ws/waiter/{waiter_id}`
App del mesero. Recibe notificación cuando su orden está lista.

```
ws://localhost:8000/orders/ws/waiter/2?token=eyJhbGc...
```

**Evento `ORDER_COMPLETED`:**
```json
{
  "event":        "ORDER_COMPLETED",
  "id":           1,
  "pizza_name":   "Pepperoni",
  "table_number": 5,
  "status":       "COMPLETED",
  "updated_at":   "2026-03-10T20:10:00"
}
```

---

## 7. Roles y permisos

| Endpoint                        | Sin token | MESERO | COCINERO | ADMIN |
|---------------------------------|:---------:|:------:|:--------:|:-----:|
| `GET /menu`                     | ✅        | ✅     | ✅       | ✅    |
| `GET /productos/`               | ✅        | ✅     | ✅       | ✅    |
| `GET /productos/{id}`           | ✅        | ✅     | ✅       | ✅    |
| `POST /productos/`              | ❌        | ❌     | ❌       | ✅    |
| `PUT /productos/{id}`           | ❌        | ❌     | ❌       | ✅    |
| `DELETE /productos/{id}`        | ❌        | ❌     | ❌       | ✅    |
| `POST /orders/`                 | ❌        | ✅     | ✅       | ✅    |
| `GET /orders/`                  | ❌        | ✅     | ✅       | ✅    |
| `PATCH /orders/{id}/status/`    | ❌        | ✅     | ✅       | ✅    |
| `GET /orders/{id}/completed/`   | ❌        | ✅     | ✅       | ✅    |
| `GET /waiters/{id}/profile/`    | ❌        | ✅     | ✅       | ✅    |
| `PATCH /waiters/{id}/profile/`  | ❌        | ✅     | ✅       | ✅    |
| `POST /waiters/{id}/photo/`     | ❌        | ✅     | ✅       | ✅    |
| `POST /ordenes/vender`          | ✅        | ✅     | ✅       | ✅    |
| `GET /ordenes/historial`        | ✅        | ✅     | ✅       | ✅    |

---

## Cómo usar el token

Después del login, incluye el token en todas las peticiones protegidas:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Para probar rápido desde consola:
```bash
# Guardar el token en variable
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"tu@email.com","password":"tu_password"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Usar el token
curl http://localhost:8000/orders/ -H "Authorization: Bearer $TOKEN"
```
