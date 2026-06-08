FROM python:3.10-slim

# Evitar que Python guarde en caché y asegurar que los logs salgan en consola
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exponemos el puerto web de Flet
EXPOSE 8000

# Comando para ejecutar la app
CMD ["python", "main.py"]