# Distrito Pizza — API REST

> **Base URL (Producción):** `http://44.212.148.188:8000`  
> **Swagger / Docs interactivos:** `http://44.212.148.188:8000/docs`  
> **Versión:** 2.0.0

---

## Índice

- [1. Autenticación](#1-autenticación)
- [2. Productos / Menú](#2-productos--menú)
- [3. Órdenes](#3-órdenes)
- [4. Perfil del mesero](#4-perfil-del-mesero)
- [5. Ventas e historial](#5-ventas-e-historial)
- [6. WebSockets](#6-websockets)
- [7. Tabla de permisos por rol](#7-tabla-de-permisos-por-rol)
- [8. Cómo usar el token JWT](#8-cómo-usar-el-token-jwt)

---

## 1. Autenticación

### `POST /auth/register`
Registra un nuevo usuario. **No requiere token.**

**URL:** `http://44.212.148.188:8000/auth/register`

**Body (JSON):**
```json
{
  "email":    "usuario@ejemplo.com",
  "name":     "Nombre Completo",
  "password": "contraseña123",
  "rol":      "MESERO"
}
```

| Campo      | Tipo   | Requerido | Valores válidos                                       |
|------------|--------|-----------|-------------------------------------------------------|
| `email`    | string | ✅        | Email válido y único                                  |
| `name`     | string | ✅        | Texto libre                                           |
| `password` | string | ✅        | Texto libre                                           |
| `rol`      | string | ❌        | `MESERO`, `COCINERO`, `ADMIN` (default: `MESERO`)    |

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
Inicia sesión y obtiene el token JWT. **No requiere token.**

**URL:** `http://44.212.148.188:8000/auth/login`

**Body (JSON):**
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

**URL:** `http://44.212.148.188:8000/menu`

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

**URL:** `http://44.212.148.188:8000/productos/`

---

### `GET /productos/{producto_id}`
Devuelve un producto por ID. **Sin autenticación.**

**URL:** `http://44.212.148.188:8000/productos/{producto_id}`

**Respuesta `200`:**
```json
{ "id": 1, "nombre": "Pepperoni", "precio": 139.0 }
```

---

### `POST /productos/` 🔒 Solo ADMIN
Crea un nuevo producto.

**URL:** `http://44.212.148.188:8000/productos/`  
**Header:** `Authorization: Bearer <token>`

**Body (JSON):**
```json
{
  "nombre": "Pizza Nueva",
  "precio": 199.0
}
```

**Respuesta `201`:**
```json
{ "id": 7, "nombre": "Pizza Nueva", "precio": 199.0 }
```

---

### `PUT /productos/{producto_id}` 🔒 Solo ADMIN
Actualiza un producto existente.

**URL:** `http://44.212.148.188:8000/productos/{producto_id}`  
**Header:** `Authorization: Bearer <token>`

**Body (JSON):** Todos los campos son opcionales.
```json
{
  "nombre": "Nuevo Nombre",
  "precio": 220.0
}
```

**Respuesta `200`:** Producto actualizado.

---

### `DELETE /productos/{producto_id}` 🔒 Solo ADMIN
Elimina un producto.

**URL:** `http://44.212.148.188:8000/productos/{producto_id}`  
**Header:** `Authorization: Bearer <token>`

**Respuesta `200`:** Confirmación de eliminación.

---

## 3. Órdenes

### `POST /orders/` 🔒 Token requerido
El mesero crea una nueva orden. Estado inicial siempre `PENDING`. Notifica automáticamente a la cocina por WebSocket.

**URL:** `http://44.212.148.188:8000/orders/`  
**Header:** `Authorization: Bearer <token>`

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

| Campo             | Tipo   | Requerido | Descripción                     |
|-------------------|--------|-----------|---------------------------------|
| `pizza_name`      | string | ✅        | Nombre de la pizza              |
| `price`           | float  | ✅        | Precio de la pizza              |
| `client_name`     | string | ✅        | Nombre del cliente              |
| `total_paid`      | float  | ✅        | Dinero entregado por el cliente |
| `change_returned` | float  | ✅        | Cambio devuelto                 |
| `table_number`    | int    | ✅        | Número de mesa                  |
| `waiter_id`       | int    | ✅        | ID del mesero                   |
| `status`          | string | ❌        | Default: `PENDING`              |

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
Devuelve órdenes activas (`PENDING` e `IN_PROGRESS`) para la pantalla de cocina.

**URL:** `http://44.212.148.188:8000/orders/`  
**Header:** `Authorization: Bearer <token>`

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
La cocina actualiza el estado de una orden.  
Flujo: `PENDING → IN_PROGRESS → COMPLETED`. Al llegar a `COMPLETED`, notifica al mesero por WebSocket.

**URL:** `http://44.212.148.188:8000/orders/{order_id}/status/`  
**Header:** `Authorization: Bearer <token>`

**Body (JSON):**
```json
{ "status": "IN_PROGRESS" }
```

| Valor         | Descripción             |
|---------------|-------------------------|
| `PENDING`     | En espera               |
| `IN_PROGRESS` | En preparación (cocina) |
| `COMPLETED`   | Lista para entregar     |

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

**URL:** `http://44.212.148.188:8000/orders/{waiter_id}/completed/`  
**Header:** `Authorization: Bearer <token>`

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

**URL:** `http://44.212.148.188:8000/waiters/{user_id}/profile/`  
**Header:** `Authorization: Bearer <token>`

**Respuesta `200`:**
```json
{
  "id": 2,
  "name": "Mesero Test",
  "phone": "0987654321",
  "email": "mesero@pizza.com",
  "photo_url": "http://44.212.148.188:8000/static/photos/foto.jpg"
}
```

---

### `PATCH /waiters/{user_id}/profile/` 🔒 Token requerido
Actualiza nombre y/o teléfono del mesero. Ambos campos son opcionales.

**URL:** `http://44.212.148.188:8000/waiters/{user_id}/profile/`  
**Header:** `Authorization: Bearer <token>`

**Body (JSON):**
```json
{
  "name":  "Nuevo Nombre",
  "phone": "0987654321"
}
```

**Respuesta `200`:** Perfil actualizado (mismo formato que GET).

---

### `POST /waiters/{user_id}/photo/` 🔒 Token requerido
Sube una foto de perfil. Máximo 5 MB. `Content-Type: multipart/form-data`.

**URL:** `http://44.212.148.188:8000/waiters/{user_id}/photo/`  
**Header:** `Authorization: Bearer <token>`

**Campo del formulario:** `photo` (archivo JPEG)

```bash
curl -X POST http://44.212.148.188:8000/waiters/2/photo/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "photo=@/ruta/a/foto.jpg"
```

**Respuesta `201`:**
```json
{
  "photo_url": "http://44.212.148.188:8000/static/photos/2_foto.jpg"
}
```

---

## 5. Ventas e historial

### `POST /ordenes/vender`
Registra una nueva venta. **Sin autenticación.**

**URL:** `http://44.212.148.188:8000/ordenes/vender`

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

**URL:** `http://44.212.148.188:8000/ordenes/historial`

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
Obtiene una venta por ID. **Sin autenticación.**

**URL:** `http://44.212.148.188:8000/ordenes/{orden_id}`

**Respuesta `200`:** Mismo formato que un item del historial.

---

### `DELETE /ordenes/{orden_id}`
Elimina una venta del historial. **Sin autenticación.**

**URL:** `http://44.212.148.188:8000/ordenes/{orden_id}`

**Respuesta `200`:** Confirmación de eliminación.

---

## 6. WebSockets

El token JWT se pasa como query parameter: `?token=<jwt>`

### `WS /orders/ws/kitchen`
Pantalla de cocina. Recibe eventos en tiempo real.

**URL:** `ws://44.212.148.188:8000/orders/ws/kitchen?token=<jwt>`

| Evento                 | Cuándo se dispara                      |
|------------------------|----------------------------------------|
| `NEW_ORDER`            | Cuando un mesero crea una orden nueva  |
| `ORDER_STATUS_CHANGED` | Cuando la cocina actualiza el estado   |

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

## 7. Tabla de permisos por rol

| Endpoint                          | Sin token | MESERO | COCINERO | ADMIN |
|-----------------------------------|:---------:|:------:|:--------:|:-----:|
| `GET /menu`                       | ✅        | ✅     | ✅       | ✅    |
| `GET /productos/`                 | ✅        | ✅     | ✅       | ✅    |
| `GET /productos/{id}`             | ✅        | ✅     | ✅       | ✅    |
| `POST /productos/`                | ❌        | ❌     | ❌       | ✅    |
| `PUT /productos/{id}`             | ❌        | ❌     | ❌       | ✅    |
| `DELETE /productos/{id}`          | ❌        | ❌     | ❌       | ✅    |
| `POST /orders/`                   | ❌        | ✅     | ✅       | ✅    |
| `GET /orders/`                    | ❌        | ✅     | ✅       | ✅    |
| `PATCH /orders/{id}/status/`      | ❌        | ✅     | ✅       | ✅    |
| `GET /orders/{id}/completed/`     | ❌        | ✅     | ✅       | ✅    |
| `GET /waiters/{id}/profile/`      | ❌        | ✅     | ✅       | ✅    |
| `PATCH /waiters/{id}/profile/`    | ❌        | ✅     | ✅       | ✅    |
| `POST /waiters/{id}/photo/`       | ❌        | ✅     | ✅       | ✅    |
| `POST /ordenes/vender`            | ✅        | ✅     | ✅       | ✅    |
| `GET /ordenes/historial`          | ✅        | ✅     | ✅       | ✅    |
| `GET /ordenes/{id}`               | ✅        | ✅     | ✅       | ✅    |
| `DELETE /ordenes/{id}`            | ✅        | ✅     | ✅       | ✅    |

---

## 8. Cómo usar el token JWT

Después del login, incluye el token en todas las peticiones protegidas:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ejemplo rápido con `curl`:**

```bash
# Guardar el token en una variable
TOKEN=$(curl -s -X POST http://44.212.148.188:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"tu@email.com","password":"tu_password"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Listar órdenes activas
curl http://44.212.148.188:8000/orders/ \
  -H "Authorization: Bearer $TOKEN"

# Crear una orden
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
```

---

> Docs interactivos completos disponibles en: **http://44.212.148.188:8000/docs**

## ✨ Características

### Autenticación y Seguridad
- ✅ Sistema de registro de usuarios con validación de email
- ✅ Login con generación de tokens JWT
- ✅ Contraseñas hasheadas con bcrypt
- ✅ Tokens con expiración configurable

### Gestión de Productos (Pizzas)
- ✅ CRUD completo de productos
- ✅ Validación de nombres únicos
- ✅ Control de precios

### Gestión de Órdenes
- ✅ Registro de ventas con cálculo automático
- ✅ Historial de órdenes completo
- ✅ Detalle de productos por orden
- ✅ Eliminación de órdenes

### Base de Datos
- ✅ PostgreSQL con SQLAlchemy ORM
- ✅ Migraciones automáticas
- ✅ Relaciones entre tablas configuradas

---

## 🏗️ Arquitectura del Proyecto

Este proyecto sigue **Clean Architecture** (Arquitectura Limpia), separando las responsabilidades en capas:

```
app/
├── data/              # Capa de Datos
│   ├── repositories/  # Acceso a base de datos
│   └── sources/       # Configuración de DB
├── domain/            # Capa de Dominio
│   ├── models/        # Modelos de SQLAlchemy
│   └── schemas/       # Schemas de Pydantic
├── presentation/      # Capa de Presentación
│   └── controllers/   # Endpoints de FastAPI
└── services/          # Capa de Lógica de Negocio
```

### Flujo de una Petición

```
Cliente → Controller → Service → Repository → Database
                ↓
             Schema (validación)
```

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **FastAPI**: Framework web moderno y rápido
- **Python 3.10**: Lenguaje de programación
- **SQLAlchemy**: ORM para manejo de base de datos
- **Pydantic**: Validación de datos
- **Uvicorn**: Servidor ASGI

### Seguridad
- **python-jose**: Generación y validación de JWT
- **passlib[bcrypt]**: Hashing de contraseñas
- **python-multipart**: Manejo de formularios

### Base de Datos
- **PostgreSQL 15**: Base de datos relacional
- **psycopg2-binary**: Driver de PostgreSQL

### DevOps
- **Docker**: Contenedorización
- **Docker Compose**: Orquestación de contenedores
- **AWS EC2**: Servidor en la nube
- **GitHub**: Control de versiones

---

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.10+
- PostgreSQL 15+
- Docker y Docker Compose (opcional)
- Git

### 1. Clonar el Repositorio

```bash
git clone https://github.com/chame1805/apiPizzeria.git
cd apiPizzeria
```

### 2. Crear Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Base de Datos
DB_USER=pizza_user
DB_PASSWORD=pizza_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pizzeria_db

# JWT
SECRET_KEY=tu_clave_secreta_muy_segura_cambiala_en_produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 días
```

### 5. Iniciar Base de Datos PostgreSQL

#### Opción A: Con Docker
```bash
docker run -d \
  --name postgres_pizzeria \
  -e POSTGRES_USER=pizza_user \
  -e POSTGRES_PASSWORD=pizza_password \
  -e POSTGRES_DB=pizzeria_db \
  -p 5432:5432 \
  postgres:15-alpine
```

#### Opción B: PostgreSQL Local
Crea la base de datos manualmente y ejecuta el archivo `init.sql`

### 6. Ejecutar la Aplicación

```bash
uvicorn main:app --reload --port 8000
```

La API estará disponible en: **http://localhost:8000**

### 7. Acceder a la Documentación

- Swagger UI: **http://localhost:8000/docs**
- ReDoc: **http://localhost:8000/redoc**

---

## 📡 Endpoints de la API

### URL Base (Producción)
```
http://44.212.148.188:8000
```

### Autenticación

#### Registro de Usuario
```http
POST /auth/register
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "nombre": "Juan Pérez",
  "password": "miPassword123"
}
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "usuario": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "nombre": "Juan Pérez",
    "fecha_registro": "2026-02-05T10:30:00"
  }
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "password": "miPassword123"
}
```

### Productos (Pizzas)

#### Listar Todos los Productos
```http
GET /productos/
```

#### Obtener un Producto
```http
GET /productos/{producto_id}
```

#### Crear Producto
```http
POST /productos/
Content-Type: application/json

{
  "nombre": "Pizza Hawaiana",
  "precio": 150.00
}
```

#### Actualizar Producto
```http
PUT /productos/{producto_id}
Content-Type: application/json

{
  "nombre": "Pizza Hawaiana Grande",
  "precio": 180.00
}
```

#### Eliminar Producto
```http
DELETE /productos/{producto_id}
```

### Órdenes

#### Crear Venta
```http
POST /ordenes/vender
Content-Type: application/json

{
  "cliente": {
    "nombre": "Juan Pérez",
    "telefono": "5551234567",
    "direccion": "Calle Principal 123"
  },
  "items": [
    {
      "producto_id": 1,
      "cantidad": 2
    },
    {
      "producto_id": 3,
      "cantidad": 1
    }
  ],
  "pago_cliente": 500.00
}
```

#### Historial de Órdenes
```http
GET /ordenes/historial
```

#### Obtener Orden Específica
```http
GET /ordenes/{orden_id}
```

#### Eliminar Orden
```http
DELETE /ordenes/{orden_id}
```

### Menú (Legacy)
```http
GET /menu
```

---

## ☁️ Despliegue en AWS

### Arquitectura de Despliegue

```
Internet → AWS EC2 (Ubuntu) → Docker Compose
                                ├── Backend (FastAPI)
                                └── PostgreSQL
```

### Pasos para Desplegar

#### 1. Configurar Instancia EC2
- Tipo: t2.micro o superior
- SO: Ubuntu Server 22.04 LTS
- Security Group: Abrir puertos 22 (SSH), 8000 (API)

#### 2. Conectarse al Servidor
```bash
ssh -i pizzeria.pem ubuntu@44.212.148.188
```

#### 3. Instalar Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```

#### 4. Instalar Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 5. Clonar Repositorio
```bash
git clone https://github.com/chame1805/apiPizzeria.git
cd apiPizzeria
```

#### 6. Crear Archivo .env
```bash
nano .env
```

Agregar las variables de entorno necesarias.

#### 7. Iniciar Contenedores
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

#### 8. Verificar Estado
```bash
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Comandos Útiles en Producción

```bash
# Actualizar código
git pull origin main

# Reconstruir contenedores
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Reiniciar servicios
docker-compose -f docker-compose.prod.yml restart

# Detener todo
docker-compose -f docker-compose.prod.yml down
```

---

## 📁 Estructura del Proyecto

```
distritPizza/
├── app/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── orden_repository.py      # Gestión de órdenes
│   │   │   ├── producto_repository.py    # Gestión de productos
│   │   │   └── usuario_repository.py     # Gestión de usuarios
│   │   └── sources/
│   │       ├── __init__.py
│   │       └── database.py               # Configuración de DB
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── models.py                 # Modelos SQLAlchemy
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── auth_schemas.py           # Schemas de autenticación
│   │       ├── producto_schemas.py        # Schemas de productos
│   │       ├── schemas.py                # Schemas generales
│   │       └── venta_schemas.py          # Schemas de ventas
│   ├── presentation/
│   │   ├── __init__.py
│   │   └── controllers/
│   │       ├── __init__.py
│   │       ├── auth_controller.py        # Endpoints de auth
│   │       ├── producto_controller.py     # Endpoints de productos
│   │       └── venta_controller.py       # Endpoints de ventas
│   └── services/
│       ├── __init__.py
│       ├── auth_service.py               # Lógica de autenticación
│       ├── producto_service.py            # Lógica de productos
│       └── venta_service.py              # Lógica de ventas
├── .env.example                          # Ejemplo de variables de entorno
├── .gitignore                            # Archivos ignorados por Git
├── DEPLOY_AWS.md                         # Guía de despliegue en AWS
├── Dockerfile                            # Imagen Docker del backend
├── docker-compose.prod.yml               # Compose para producción
├── docker-compose.yml                    # Compose para desarrollo
├── init.sql                              # Script de inicialización de DB
├── main.py                               # Punto de entrada de la API
├── README.md                             # Este archivo
└── requirements.txt                      # Dependencias de Python
```

---

## 🔧 Desarrollo

### Agregar Nuevas Funcionalidades

1. **Crear el Schema** en `app/domain/schemas/`
2. **Crear el Repository** en `app/data/repositories/`
3. **Crear el Service** en `app/services/`
4. **Crear el Controller** en `app/presentation/controllers/`
5. **Registrar el Router** en `main.py`

### Ejecutar Tests Localmente

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar la aplicación
uvicorn main:app --reload --port 8001

# Probar endpoints
curl http://localhost:8001/docs
```

---

## 📝 Notas Importantes

### Problemas Comunes y Soluciones

#### Error de bcrypt
Si ves el error `password cannot be longer than 72 bytes`:
- Ya está solucionado en el código actual
- El servicio trunca automáticamente las contraseñas

#### Puerto 8000 bloqueado en AWS
- Ve a AWS Console → EC2 → Security Groups
- Agrega regla de entrada: Puerto 8000, Origen 0.0.0.0/0

#### Contenedores no inician
```bash
# Ver logs detallados
docker-compose -f docker-compose.prod.yml logs -f

# Reconstruir completamente
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🎯 Próximas Mejoras

- [ ] Agregar paginación en el historial de órdenes
- [ ] Implementar roles de usuario (Admin, Cajero)
- [ ] Agregar endpoints protegidos con JWT
- [ ] Implementar WebSockets para notificaciones en tiempo real
- [ ] Agregar sistema de reportes
- [ ] Integración con pasarelas de pago
- [ ] App móvil con Flutter/React Native

---

## 👤 Autor

**Proyecto desarrollado por:** Angel

**Repositorio:** [github.com/chame1805/apiPizzeria](https://github.com/chame1805/apiPizzeria)

**Deployed API:** [http://44.212.148.188:8000/docs](http://44.212.148.188:8000/docs)

---

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

## 🙏 Agradecimientos

- FastAPI por su excelente documentación
- La comunidad de Python
- AWS por el tier gratuito
- Docker por facilitar el despliegue

---

## 📞 Soporte

Para reportar bugs o solicitar features, abre un issue en GitHub:
[https://github.com/chame1805/apiPizzeria/issues](https://github.com/chame1805/apiPizzeria/issues)

---

**¡Gracias por usar Pizzería API!** 🍕
