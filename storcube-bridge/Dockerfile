ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.11-alpine3.18
FROM ${BUILD_FROM}

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
WORKDIR /usr/src/app
COPY . .

# Droits d'exécution pour le script de lancement
RUN chmod a+x run.sh

CMD [ "./run.sh" ]
