FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Railway provides PORT; must listen on 0.0.0.0, not localhost
CMD gunicorn --bind 0.0.0.0:${PORT:-8000} app:app
