FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir \
    requests \
    google-auth \
    google-auth-oauthlib \
    google-auth-httplib2 \
    flask \
    flask_sqlalchemy \
    python-dotenv \
    flask-cors

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
