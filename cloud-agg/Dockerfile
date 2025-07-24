FROM python:3.12-slim
LABEL authors="quietxo"

RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*
RUN pip install paho-mqtt
COPY app.py /app/app.py
CMD ["python", "/app/app.py"]