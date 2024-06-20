FROM python:3.8-slim

# Встановлення необхідних системних пакетів
RUN apt-get update && apt-get install -y \
    build-essential \
    libpcre3 \
    libpcre3-dev \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Створення робочої директорії
WORKDIR /eva00

# Копіювання requirements.txt
COPY requirements.txt /eva00/requirements.txt

# Встановлення залежностей
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання всіх файлів проекту
COPY . /eva00

# Відкриття порту
EXPOSE 8000

# Запуск Sanic сервера
CMD ["python", "app.py"]
