FROM python:3.10.10-slim-bullseye

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
COPY config.py.docker config.py

ENV FLASK_ENV=production
ENV FLASK_DEBUG=False
EXPOSE 4856

CMD ["gunicorn", "-w", "2", "-k", "gthread", "-b", "0.0.0.0:4856", "app:app"]
