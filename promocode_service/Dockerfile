FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем весь сервис внутрь контейнера в /app
COPY . /app


# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем gRPC сервер
CMD ["python", "grpc_server.py"]




