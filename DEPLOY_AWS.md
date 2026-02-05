# Guía de Despliegue en AWS EC2

## 📋 Requisitos previos
- Cuenta de AWS
- Git instalado localmente
- Código subido a GitHub

## 🚀 Pasos para desplegar

### 1️⃣ Crear instancia EC2

1. **Entra a AWS Console** → EC2 → "Launch Instance"

2. **Configuración:**
   - **Name:** distritPizza-backend
   - **AMI:** Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance type:** t2.micro (Free tier) o t2.small (recomendado)
   - **Key pair:** Crea o selecciona una key pair (.pem)
   - **Security Group:** Configura estos puertos:
     - SSH (22) - Tu IP
     - HTTP (80) - Anywhere
     - Custom TCP (8000) - Anywhere (para la API)
     - Custom TCP (5432) - Anywhere (PostgreSQL, opcional)

3. **Launch instance** y espera que esté "Running"

### 2️⃣ Conectarte a la instancia

```bash
# Dar permisos a la key
chmod 400 tu-key.pem

# Conectar por SSH
ssh -i tu-key.pem ubuntu@TU_IP_PUBLICA_EC2
```

### 3️⃣ Instalar Docker en EC2

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Añadir usuario al grupo docker
sudo usermod -aG docker ubuntu

# Instalar Docker Compose
sudo apt install docker-compose -y

# Verificar instalación
docker --version
docker-compose --version

# IMPORTANTE: Cerrar y volver a conectar por SSH
exit
```

Vuelve a conectarte:
```bash
ssh -i tu-key.pem ubuntu@TU_IP_PUBLICA_EC2
```

### 4️⃣ Clonar tu repositorio

```bash
# Clonar el proyecto
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO
```

### 5️⃣ Configurar variables de entorno

```bash
# Crear archivo .env basado en el ejemplo
cp .env.example .env

# Editar con nano
nano .env
```

**Configuración importante en .env:**
```env
DB_USER=postgres_user
DB_PASSWORD=TU_PASSWORD_SEGURO_AQUI
DB_HOST=db
DB_PORT=5432
DB_NAME=distritpizza_db

SECRET_KEY=GENERA_UNA_CLAVE_SUPER_SEGURA_AQUI
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

ENVIRONMENT=production
```

💡 **Generar SECRET_KEY segura:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Guarda con: `Ctrl + X` → `Y` → `Enter`

### 6️⃣ Iniciar la aplicación

```bash
# Dar permisos al script de despliegue
chmod +x deploy.sh

# Ejecutar despliegue
./deploy.sh
```

O manualmente:
```bash
# Iniciar servicios
docker-compose -f docker-compose.prod.yml up -d

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 7️⃣ Verificar que funciona

Abre en tu navegador:
```
http://TU_IP_PUBLICA_EC2:8000/docs
```

Deberías ver la documentación Swagger de tu API.

## 🔄 Para actualizar después

```bash
# Conectar por SSH
ssh -i tu-key.pem ubuntu@TU_IP_PUBLICA_EC2

# Ir al proyecto
cd TU_REPO

# Ejecutar script de despliegue
./deploy.sh
```

## 🛠️ Comandos útiles

```bash
# Ver contenedores corriendo
docker ps

# Ver logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f backend

# Reiniciar servicios
docker-compose -f docker-compose.prod.yml restart

# Detener todo
docker-compose -f docker-compose.prod.yml down

# Ver uso de recursos
docker stats
```

## 🔒 Configurar HTTPS (Opcional pero recomendado)

Si quieres usar un dominio con HTTPS:

1. Compra un dominio (o usa uno gratis de Freenom)
2. Apunta el dominio a tu IP de EC2
3. Instala Nginx y Certbot
4. Configura reverse proxy

## 📊 Monitoreo

Para ver si todo está corriendo bien:

```bash
# Estado de contenedores
docker-compose -f docker-compose.prod.yml ps

# Logs de la base de datos
docker-compose -f docker-compose.prod.yml logs db

# Logs del backend
docker-compose -f docker-compose.prod.yml logs backend

# Entrar al contenedor
docker exec -it backend_python bash
```

## ⚠️ Troubleshooting

**Problema:** No puedo acceder a la API
- Verifica Security Groups en AWS (puerto 8000 abierto)
- Verifica que los contenedores estén corriendo: `docker ps`
- Revisa logs: `docker-compose logs backend`

**Problema:** Error de base de datos
- Verifica que el contenedor de PostgreSQL esté corriendo
- Revisa el archivo .env
- Revisa logs: `docker-compose logs db`

**Problema:** "Permission denied"
- Usa `sudo` antes del comando
- O añade tu usuario al grupo docker: `sudo usermod -aG docker $USER`

## 💰 Costos estimados

- **t2.micro (Free Tier):** Gratis el primer año, después ~$8/mes
- **t2.small:** ~$17/mes
- **Storage:** ~$1-2/mes por 10GB

## 🎯 Endpoints disponibles

Una vez desplegado:

- `GET http://TU_IP:8000/` - Root
- `GET http://TU_IP:8000/docs` - Documentación Swagger
- `GET http://TU_IP:8000/menu` - Menú de productos
- `POST http://TU_IP:8000/auth/register` - Registro
- `POST http://TU_IP:8000/auth/login` - Login
- `POST http://TU_IP:8000/ventas` - Crear venta

---

**✅ ¡Listo! Tu API está en producción en AWS**
