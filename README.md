# Distrito Pizza — API REST

> **Base URL (Producción):** `http://44.212.148.188:8000`
> **Swagger / Docs interactivos:** `http://44.212.148.188:8000/docs`
> **Versión:** 2.0.0

---

## Índice

- [Arquitectura](#arquitectura)
- [Tecnologías](#tecnologías)
- [Levantar el proyecto](#levantar-el-proyecto)
- [Variables de entorno](#variables-de-entorno)
- [1. Autenticación](#1-autenticación)
- [2. Productos / Menú](#2-productos--menú)
- [3. Órdenes](#3-órdenes)
- [4. Perfil del mesero](#4-perfil-del-mesero)
- [5. Notificaciones push móvil (FCM)](#5-notificaciones-push-móvil-fcm)
- [6. Sensores móviles](#6-sensores-móviles)
- [7. Ventas e historial (legacy)](#7-ventas-e-historial-legacy)
- [8. WebSockets](#8-websockets)
- [9. Tabla de permisos por rol](#9-tabla-de-permisos-por-rol)
- [10. Usar el token JWT](#10-usar-el-token-jwt)

---

## Arquitectura

El proyecto sigue **Clean Architecture** separando responsabilidades en capas:

```
app/
├── core/                  # Configuración transversal (seguridad, Firebase, WebSocket manager)
├── data/
│   ├── repositories/      # Acceso a base de datos
│   └── sources/           # Configuración de la conexión a DB
├── domain/
│   ├── models/            # Modelos SQLAlchemy (tablas)
│   └── schemas/           # Schemas Pydantic (validación / serialización)
├── presentation/
│   └── controllers/       # Endpoints FastAPI (routers)
└── services/              # Lógica de negocio
```

Flujo de una petición:

```
Cliente → Controller → Service → Repository → PostgreSQL
               ↓
          Schema (validación Pydantic)
```

---

## Tecnologías

| Capa | Librería |
|------|----------|
| Framework web | FastAPI + Uvicorn |
| ORM | SQLAlchemy |
| Base de datos | PostgreSQL 15 |
| Autenticación | JWT (python-jose) + bcrypt (passlib) |
| WebSockets | FastAPI nativo (websockets) |
| Push notifications | Firebase Admin SDK (firebase-admin) |
| Contenedores | Docker + Docker Compose |

---

## Levantar el proyecto

### Desarrollo local (Docker)

```bash
# Clonar
git clone https://github.com/chame1805/apiPizzeria.git
cd apiPizzeria

# Crear .env (ver sección Variables de entorno)
cp .env.example .env
# Editar .env con tus valores

# Levantar
docker-compose up --build
```

La API queda disponible en `http://localhost:8000`.

### Producción (AWS EC2)

```bash
docker-compose -f docker-compose.prod.yml up -d --build

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Actualizar código
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## Variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Base de Datos
DB_USER=mi_usuario
DB_PASSWORD=mi_password
DB_HOST=db
DB_PORT=5432
DB_NAME=mi_base_de_datos

# JWT
SECRET_KEY=clave_secreta_muy_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Firebase Cloud Messaging (opcional — si no se configura, las push no se envían)
FIREBASE_PROJECT_ID=pizzas-287e6
FIREBASE_CREDENTIALS_FILE=firebase-service-account.json
```

El archivo `firebase-service-account.json` se descarga desde Firebase Console → Configuración del proyecto → Cuentas de servicio → Generar nueva clave privada.

---

## 1. Autenticación

### `POST /auth/register`
Registra un nuevo usuario. **Sin autenticación.**

**Body:**
```json
{
  "email":    "usuario@ejemplo.com",
  "name":     "Nombre Completo",
  "password": "contraseña123",
  "rol":      "MESERO"
}
```

| Campo | Tipo | Requerido | Valores válidos |
|-------|------|-----------|-----------------|
| `email` | string | ✅ | Email único válido |
| `name` | string | ✅ | Texto libre |
| `password` | string | ✅ | Texto libre |
| `rol` | string | ❌ | `MESERO`, `COCINERO`, `ADMIN` (default: `MESERO`) |

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
Inicia sesión y obtiene el token JWT. **Sin autenticación.**

**Body:**
```json
{
  "email":    "usuario@ejemplo.com",
  "password": "contraseña123"
}
```

**Respuesta `200`:** Mismo formato que `/auth/register`.
**Error `401`:** Credenciales incorrectas.

---

## 2. Productos / Menú

### `GET /menu`
Lista todos los productos. **Sin autenticación.**

**Respuesta `200`:**
```json
[
  { "id": 1, "nombre": "Pepperoni", "precio": 139.0 },
  { "id": 2, "nombre": "Hawaiana",  "precio": 159.0 }
]
```

---

### `GET /productos/`
Igual que `/menu`. Sin autenticación.

### `GET /productos/{producto_id}`
Devuelve un producto por ID. Sin autenticación.

### `POST /productos/` — Solo ADMIN
Crea un nuevo producto. Requiere `Authorization: Bearer <token>`.

**Body:** `{ "nombre": "Pizza Nueva", "precio": 199.0 }`

### `PUT /productos/{producto_id}` — Solo ADMIN
Actualiza un producto. Requiere token.

### `DELETE /productos/{producto_id}` — Solo ADMIN
Elimina un producto. Requiere token.

---

## 3. Órdenes

### `POST /orders/` — Token requerido
El mesero crea una nueva orden. Estado inicial siempre `PENDING`. Notifica automáticamente a cocina por WebSocket.

**Body:**
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

**Respuesta `201`:**
```json
{
  "id":              1,
  "pizza_name":      "Pepperoni",
  "price":           139.0,
  "client_name":     "Juan Pérez",
  "total_paid":      200.0,
  "change_returned": 61.0,
  "waiter_id":       2,
  "table_number":    5,
  "status":          "PENDING",
  "created_at":      "2026-03-10T20:00:00",
  "updated_at":      "2026-03-10T20:00:00"
}
```

---

### `GET /orders/` — Token requerido
Devuelve las órdenes del mesero autenticado con su estado actual.

---

### `GET /orders/kitchen/active/` — Token requerido
Devuelve las órdenes activas (`PENDING` e `IN_PROGRESS`) para la pantalla de cocina.

**Respuesta `200`:**
```json
[
  {
    "id":           1,
    "pizza_name":   "Pepperoni",
    "table_number": 5,
    "client_name":  "Juan Pérez",
    "status":       "PENDING",
    "created_at":   "2026-03-10T20:00:00"
  }
]
```

---

### `PATCH /orders/{order_id}/status/` — Token requerido
La cocina actualiza el estado de una orden.

Flujo de estados: `PENDING → IN_PROGRESS → COMPLETED`

Al pasar a `COMPLETED`:
- Se notifica al mesero por **WebSocket**
- Se envía una **notificación push FCM** al dispositivo del mesero (si Firebase está configurado)

**Body:**
```json
{ "status": "IN_PROGRESS" }
```

**Respuesta `200`:**
```json
{
  "id":         1,
  "status":     "IN_PROGRESS",
  "updated_at": "2026-03-10T20:05:00"
}
```

---

### `GET /orders/{waiter_id}/completed/` — Token requerido
Devuelve todas las órdenes `COMPLETED` de un mesero. Útil como historial o fallback si el WebSocket se desconecta.

---

## 4. Perfil del mesero

### `GET /waiters/{user_id}/profile/` — Token requerido

**Respuesta `200`:**
```json
{
  "id":        2,
  "name":      "Mesero Test",
  "phone":     "0987654321",
  "email":     "mesero@pizza.com",
  "photo_url": "http://44.212.148.188:8000/static/photos/foto.jpg"
}
```

---

### `PATCH /waiters/{user_id}/profile/` — Token requerido
Actualiza nombre y/o teléfono. Ambos campos opcionales.

**Body:**
```json
{
  "name":  "Nuevo Nombre",
  "phone": "0987654321"
}
```

---

### `POST /waiters/{user_id}/photo/` — Token requerido
Sube foto de perfil. Máximo 5 MB. `Content-Type: multipart/form-data`.

**Campo del formulario:** `photo` (archivo JPEG/PNG)

**Respuesta `201`:**
```json
{
  "photo_url": "http://44.212.148.188:8000/static/photos/2_foto.jpg"
}
```

---

## 5. Notificaciones push móvil (FCM)

El backend usa **Firebase Cloud Messaging** para enviar notificaciones push a los dispositivos Android de los meseros.

### Flujo completo

```
1. Mesero hace login en la app Android
2. App obtiene el token FCM del dispositivo
3. App registra el token → POST /mobile/push-tokens/
4. Cocina marca orden como COMPLETED → PATCH /orders/{id}/status/
5. Backend busca el token FCM del mesero en BD
6. Backend envía notificación push via Firebase Admin SDK
7. App Android recibe la notificación aunque esté en segundo plano
```

---

### `POST /mobile/push-tokens/` — Token requerido
Registra o actualiza el token FCM del dispositivo del usuario autenticado.

**Body:**
```json
{
  "token":    "fcm_token_del_dispositivo",
  "platform": "ANDROID"
}
```

**Respuesta `201`:**
```json
{
  "id":         1,
  "user_id":    2,
  "token":      "fcm_token_del_dispositivo",
  "platform":   "ANDROID",
  "is_active":  true,
  "created_at": "2026-03-10T20:00:00"
}
```

---

### `DELETE /mobile/push-tokens/?token=<fcm_token>` — Token requerido
Elimina el token FCM del usuario autenticado (útil al hacer logout).

**Respuesta `200`:**
```json
{
  "deleted": true,
  "token":   "fcm_token_del_dispositivo"
}
```

---

### Notificación que recibe el mesero

Cuando la cocina marca una orden como `COMPLETED`, el dispositivo del mesero recibe:

```
Título: "Orden lista"
Cuerpo: "Pepperoni de mesa 5 está COMPLETED"

Data payload:
{
  "event":        "ORDER_COMPLETED",
  "order_id":     "1",
  "pizza_name":   "Pepperoni",
  "table_number": "5",
  "status":       "COMPLETED"
}
```

---

## 6. Sensores móviles

Endpoints para guardar y consultar datos de sensores del dispositivo (GPS y acelerómetro).

### `POST /mobile/location/` — Token requerido
Guarda una lectura GPS del usuario autenticado.

**Body:**
```json
{
  "latitude":        19.4326,
  "longitude":      -99.1332,
  "accuracy_meters": 10.5,
  "speed_mps":       1.2,
  "heading_degrees": 90.0,
  "altitude_meters": 2240.0,
  "captured_at":    "2026-03-10T20:00:00Z"
}
```

### `GET /mobile/location/latest/` — Token requerido
Devuelve la última ubicación GPS del usuario autenticado.

---

### `POST /mobile/motion-events/` — Token requerido
Guarda un evento del acelerómetro.

**Body:**
```json
{
  "axis_x":         0.12,
  "axis_y":         0.34,
  "axis_z":         9.81,
  "magnitude":      9.82,
  "is_significant": true,
  "source":         "ACCELEROMETER",
  "captured_at":   "2026-03-10T20:00:00Z"
}
```

### `GET /mobile/motion-events/latest/` — Token requerido
Devuelve el último evento de acelerómetro del usuario autenticado.

---

## 7. Ventas e historial (legacy)

Endpoints del sistema original de ventas, sin autenticación.

### `POST /ordenes/vender`

**Body:**
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

### `GET /ordenes/historial`
Devuelve el historial completo de ventas.

### `GET /ordenes/{orden_id}`
Obtiene una venta por ID.

### `DELETE /ordenes/{orden_id}`
Elimina una venta.

---

## 8. WebSockets

El token JWT se pasa como query parameter: `?token=<jwt>`

### `WS /orders/ws/kitchen`
Pantalla de cocina. Recibe eventos en tiempo real.

**URL:** `ws://44.212.148.188:8000/orders/ws/kitchen?token=<jwt>`

| Evento | Cuándo se dispara |
|--------|-------------------|
| `NEW_ORDER` | Mesero crea una orden nueva |
| `ORDER_STATUS_CHANGED` | Cocina actualiza el estado |

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

**URL:** `ws://44.212.148.188:8000/orders/ws/waiter/{waiter_id}?token=<jwt>`

El token debe pertenecer al mismo `waiter_id` del path — el servidor valida esto.

**Evento `ORDER_STATUS_CHANGED`** (cualquier cambio de estado):
```json
{
  "event":        "ORDER_STATUS_CHANGED",
  "id":           1,
  "status":       "IN_PROGRESS",
  "pizza_name":   "Pepperoni",
  "table_number": 5,
  "updated_at":   "2026-03-10T20:05:00"
}
```

**Evento `ORDER_COMPLETED`** (cuando la orden queda lista):
```json
{
  "event":           "ORDER_COMPLETED",
  "id":              1,
  "pizza_name":      "Pepperoni",
  "price":           139.0,
  "total_paid":      200.0,
  "change_returned": 61.0,
  "table_number":    5,
  "status":          "COMPLETED",
  "updated_at":      "2026-03-10T20:10:00"
}
```

---

## 9. Tabla de permisos por rol

| Endpoint | Sin token | MESERO | COCINERO | ADMIN |
|----------|:---------:|:------:|:--------:|:-----:|
| `GET /menu` | ✅ | ✅ | ✅ | ✅ |
| `GET /productos/` | ✅ | ✅ | ✅ | ✅ |
| `POST /productos/` | ❌ | ❌ | ❌ | ✅ |
| `PUT /productos/{id}` | ❌ | ❌ | ❌ | ✅ |
| `DELETE /productos/{id}` | ❌ | ❌ | ❌ | ✅ |
| `POST /orders/` | ❌ | ✅ | ✅ | ✅ |
| `GET /orders/` | ❌ | ✅ | ✅ | ✅ |
| `GET /orders/kitchen/active/` | ❌ | ✅ | ✅ | ✅ |
| `PATCH /orders/{id}/status/` | ❌ | ✅ | ✅ | ✅ |
| `GET /orders/{id}/completed/` | ❌ | ✅ | ✅ | ✅ |
| `GET /waiters/{id}/profile/` | ❌ | ✅ | ✅ | ✅ |
| `PATCH /waiters/{id}/profile/` | ❌ | ✅ | ✅ | ✅ |
| `POST /waiters/{id}/photo/` | ❌ | ✅ | ✅ | ✅ |
| `POST /mobile/push-tokens/` | ❌ | ✅ | ✅ | ✅ |
| `DELETE /mobile/push-tokens/` | ❌ | ✅ | ✅ | ✅ |
| `POST /mobile/location/` | ❌ | ✅ | ✅ | ✅ |
| `GET /mobile/location/latest/` | ❌ | ✅ | ✅ | ✅ |
| `POST /mobile/motion-events/` | ❌ | ✅ | ✅ | ✅ |
| `GET /mobile/motion-events/latest/` | ❌ | ✅ | ✅ | ✅ |
| `POST /ordenes/vender` | ✅ | ✅ | ✅ | ✅ |
| `GET /ordenes/historial` | ✅ | ✅ | ✅ | ✅ |

---

## 10. Usar el token JWT

Incluye el token en el header de todas las peticiones protegidas:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ejemplo rápido con curl:**

```bash
# Login y guardar token
TOKEN=$(curl -s -X POST http://44.212.148.188:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"tu@email.com","password":"tu_password"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Crear orden
curl -X POST http://44.212.148.188:8000/orders/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pizza_name": "Pepperoni",
    "price": 139.0,
    "client_name": "Juan Pérez",
    "total_paid": 200.0,
    "change_returned": 61.0,
    "table_number": 5,
    "waiter_id": 2
  }'

# Registrar token FCM
curl -X POST http://44.212.148.188:8000/mobile/push-tokens/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"token":"fcm_token_aqui","platform":"ANDROID"}'
```

---

**Docs interactivos completos:** `http://44.212.148.188:8000/docs`

**Autor:** Angel de Jesus Chame Vera — [github.com/chame1805/apiPizzeria](https://github.com/chame1805/apiPizzeria)
