FROM python:3.11-slim

WORKDIR /app/app

COPY app/prod-requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r prod-requirements.txt

WORKDIR /app

COPY . .

ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV GUNICORN_WORKERS=4
ENV GUNICORN_THREADS=2
ENV GUNICORN_BIND=0.0.0.0:5000

EXPOSE 5000

CMD ["bash", "-c", \
    "sleep 5 && \
     cd /app/app && \
     alembic upgrade head && \
     cd .. && \
     gunicorn --workers 4 --threads 2 --bind 0.0.0.0:5000 --access-logfile - main:app"]
