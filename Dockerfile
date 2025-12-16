FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создаем не-root пользователя для безопасности
RUN useradd -m -u 1000 botuser
USER botuser

CMD ["python", "-m", "bot.main"]