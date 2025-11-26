# Usa una imagen base de Python
FROM python:3.11-slim-bullseye

# Configura DEBIAN_FRONTEND para instalaciones no interactivas
ENV DEBIAN_FRONTEND=noninteractive
# Instala dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# Configura el entorno
WORKDIR /app

# Copia el archivo de requisitos e instala las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Expone el puerto que usará Uvicorn
EXPOSE 8000

# Comando para iniciar la aplicación
# Render usará este comando por defecto para iniciar el servicio web
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
