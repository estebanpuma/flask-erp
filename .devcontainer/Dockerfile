# Usa la imagen oficial de Python como base
FROM python:3.12.6-slim

# Instala algunas dependencias básicas que podrían ser necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo requirements.txt al contenedor
COPY requirements.txt .

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Instala extensiones útiles para debugging (opcional)
RUN pip install debugpy

# Copia el código fuente de la aplicación al contenedor
COPY . .

# Expone el puerto de Flask
EXPOSE 5000

# Comando predeterminado para ejecutar la aplicación
CMD ["flask", "run", "--host=0.0.0.0"]
