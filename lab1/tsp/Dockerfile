# Dockerfile
FROM python:3.12

WORKDIR /tsp

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "tsp.wsgi:application", "--bind", "0.0.0.0:8000"]