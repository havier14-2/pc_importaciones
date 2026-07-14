# 1. Usar una imagen oficial de Python ligera
FROM python:3.9-slim

# 2. Configurar la carpeta de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar el archivo de librerías al contenedor
COPY requirements.txt .

# 4. Instalar las dependencias (el molino, la balanza, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar absolutamente todo tu código al contenedor
COPY . .

# 6. Exponer los puertos para que el profesor pueda ver la app
EXPOSE 8000 8050