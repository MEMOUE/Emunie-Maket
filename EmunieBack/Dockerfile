FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système pour mysqlclient
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collecte des fichiers statiques
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "EmunieBack.wsgi:application", "--bind", "0.0.0.0:8000"]