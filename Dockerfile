# Usamos una versión ligera de Python
FROM python:3.10-slim

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2 (driver de postgres)
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

# Copiar requirements e instalar librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Comando para iniciar la app (host 0.0.0.0 es obligatorio en Docker)
# En producción, sin --reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]