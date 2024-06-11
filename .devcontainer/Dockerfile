# Usamos una imagen base de Python
FROM python:3.8-slim-buster

# Configuramos el directorio de trabajo
WORKDIR /app

# Copiamos los archivos de requerimientos de Python
COPY requirements.txt .

# Instalamos los requerimientos de Python
RUN pip install -r requirements.txt

# Copiamos el resto de los archivos del proyecto
COPY . .

# Exponemos el puerto en el que se ejecutará la aplicación
EXPOSE 8000

# Configuramos el comando por defecto para ejecutar
CMD ["python", "src/app.py"]