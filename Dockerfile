# Usamos una imagen base oficial de Python 3.12.6
FROM python:3.12.11-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app


# Copiamos el archivo requirements.txt y lo instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código de la aplicación dentro del contenedor
COPY . .

# Establecemos la variable de entorno para que Flask funcione correctamente
ENV FLASK_APP=run.py

# Abrimos el puerto que Flask va a usar (5000)
EXPOSE 5000

# Comando para ejecutar la aplicación Flask
CMD ["flask", "run", "--host=0.0.0.0"]
