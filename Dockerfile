# Usa una imagen base de Python
FROM python:3.11-slim-bullseye

# Configura DEBIAN_FRONTEND para instalaciones no interactivas
ENV DEBIAN_FRONTEND=noninteractive
# Acepta la licencia de msodbcsql18 de forma no interactiva
ENV ACCEPT_EULA=Y

# Instala dependencias del sistema para aioodbc y SQL Server ODBC Driver
# Basado en la documentación de Microsoft para Debian/Ubuntu
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg \
    unixodbc-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Importa la clave GPG de Microsoft
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

# Añade el repositorio de Microsoft para SQL Server
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Actualiza e instala el driver ODBC 18 para SQL Server
# Auto-acepta la licencia de msodbcsql18
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
    msodbcsql18 \
    # mssql-tools18 # Opcional: si necesitas herramientas como sqlcmd
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
