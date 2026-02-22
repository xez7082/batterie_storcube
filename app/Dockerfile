FROM python:3.11-slim

WORKDIR /usr/src/app

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du script
COPY batteryMqtt.py .

# Force l'affichage des logs Python dans la console Docker
ENV PYTHONUNBUFFERED=1

CMD ["python", "./batteryMqtt.py"]
