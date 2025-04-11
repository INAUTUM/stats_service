FROM python:3.11-slim

# Создание пользователя (для production)
RUN addgroup --system --gid 1000 appuser && \
    adduser --system --uid 1000 --gid 1000 appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Для разработки запускаем от root
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]