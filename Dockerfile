FROM python:3.11-slim

WORKDIR /app

COPY prod-requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r prod-requirements.txt

COPY . .

ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV GUNICORN_WORKERS=4
ENV GUNICORN_THREADS=2
ENV GUNICORN_BIND=0.0.0.0:5000

EXPOSE 5000

CMD ["gunicorn", "--workers", "4", "--threads", "2", "--bind", "0.0.0.0:5000", "app:app"]