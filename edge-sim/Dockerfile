FROM python:3.12-slim
LABEL authors="quietxo"

RUN pip install paho-mqtt
COPY main.py /app/main.py
CMD ["python", "/app/main.py"]
