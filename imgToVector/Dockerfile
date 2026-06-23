# Usar una imagen base de Python ligera
FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /code

# Copiar e instalar las dependencias
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copiar el código de la aplicación
COPY ./app /code/app

# Hugging Face Spaces requiere que la app corra en el puerto 7860
EXPOSE 7860

# Comando para iniciar el servidor FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
