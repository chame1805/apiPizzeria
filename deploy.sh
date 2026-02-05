#!/bin/bash

# Script de despliegue para AWS EC2
# Ejecutar este script en el servidor EC2 después de clonar el repositorio

set -e  # Detener si hay algún error

echo "🚀 Iniciando despliegue..."

# 1. Actualizar código desde Git
echo "📦 Actualizando código..."
git pull origin main

# 2. Detener contenedores existentes
echo "🛑 Deteniendo contenedores..."
docker-compose -f docker-compose.prod.yml down

# 3. Construir imágenes
echo "🔨 Construyendo imágenes..."
docker-compose -f docker-compose.prod.yml build --no-cache

# 4. Iniciar servicios
echo "▶️  Iniciando servicios..."
docker-compose -f docker-compose.prod.yml up -d

# 5. Ver logs
echo "📋 Verificando logs..."
docker-compose -f docker-compose.prod.yml logs --tail=50

echo "✅ Despliegue completado!"
echo "🌐 API disponible en http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
