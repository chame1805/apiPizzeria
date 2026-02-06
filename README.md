# 🍕 Pizzería API - Proyecto FastAPI con Clean Architecture

API RESTful completa para gestión de pizzería con autenticación JWT, CRUD de productos y manejo de órdenes. Desarrollada con FastAPI siguiendo Clean Architecture y desplegada en AWS EC2 con Docker.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Arquitectura del Proyecto](#arquitectura-del-proyecto)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Instalación y Configuración](#instalación-y-configuración)
- [Endpoints de la API](#endpoints-de-la-api)
- [Despliegue en AWS](#despliegue-en-aws)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Contribución](#contribución)

---

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
